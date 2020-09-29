import logging
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Tuple, Union

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telegram import ReplyKeyboardMarkup

from today_weather.config import CONFIG, DATABASE_URI
from today_weather.exceptions import BackendError
from today_weather.models import Base, Locality, User
from today_weather.utils.misc import log_reply
from today_weather.utils.recommend import Recommender


class HandlerBase(ABC):
    """
    Base class for update handlers.
    
    Upon receiving an update, the dispatcher passes the update and context
    to the approproate registered update handler.
    """

    def __init__(self, update, context):
        """
        Sets up attributes needed to process the update and processes
        the update, all within a separate db session.
        """
        with self._db_session():
            self.update, self.context, self.message = (
                update,
                context,
                update.message.text,
            )
            self.user = self._get_or_create_user(self.update.message.from_user.id)
            self.process()

    @abstractmethod
    def process(self):
        pass

    def reply(self, **kwargs):
        self.update.message.reply_text(**kwargs)
        log_reply(self.user.id, kwargs)

    @contextmanager
    def _db_session(self):
        """
        Context manager to set up and tear down a db session.
        """
        engine = create_engine(DATABASE_URI)
        Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)
        self.session = Session()
        yield
        self.session.commit()

    def _get_or_create_user(self, id):
        user = self.session.query(User).filter(User.id == id).one_or_none()
        if not user:
            user = User(id=id)
            self.session.add(user)
            self.session.commit()
        return user


class HandlerWelcome(HandlerBase):
    """
    Welcoming message.
    """

    def process(self):
        self.reply(text=CONFIG["MESSAGES"]["WELCOME"])


class HandlerInputBase(HandlerBase):
    """
    Base class for text input handlers.
    """

    def process(self):
        logging.info(
            f"message from {self.user.id}, {self.update.message.from_user.username}: "
            f"{self.message}"
        )
        self._process()

    def _reply_with_forecast(self, locality: Union[str, int]) -> None:
        """
        Reply to the user with a weather forecast for a locality, either 
        geocoded from free form string input or referenced by id.
        """
        forecast, locality = self._get_forecast(locality)
        text = Recommender(forecast)() + "-" * 30 + f"\n{locality['name']}"
        self.reply(text=text, reply_markup=self._keyboard())
        self.user.latest_locality_id, self.user.latest_locality_name = (
            locality["links"]["self"][len("/localities/") :],
            locality["name"],
        )

    def _get_forecast(self, locality: Union[Locality, str]) -> Tuple[dict, dict]:
        """
        Call the backend to get forecast from string or locality id.
        """
        if isinstance(locality, Locality):
            response = requests.get(
                CONFIG["BACKEND_API"]["URL"] + f"/localities/{locality.id}/forecast"
            )
        else:
            response = requests.post(
                CONFIG["BACKEND_API"]["URL"] + "/localities", json={"address": locality}
            )
        if "error" not in response.json():
            forecast, locality = (
                response.json()["forecast"],
                response.json()["locality"],
            )
            return forecast, locality
        else:
            error = response.json()["error"]
            self.reply(text=error)
            raise BackendError(error)

    def _keyboard(self):
        _keyboard = [
            [CONFIG["KEYBOARD"]["REPEAT"]],
            [CONFIG["KEYBOARD"]["SET_DEFAULT"]],
        ]
        if self.user.default_locality_name is not None:
            _keyboard.append([f"Default: {self.user.default_locality_name}"])
        return ReplyKeyboardMarkup(_keyboard, resize_keyboard=True)


class HandlerAddressInput(HandlerInputBase):
    """
    Free form address input.
    """

    def _process(self):
        self._reply_with_forecast(self.message)


class HandlerCommandRepeat(HandlerInputBase):
    """
    Command to repeat the latest input.
    """

    def _process(self):
        self._reply_with_forecast(Locality(self.user.latest_locality_id))


class HandlerCommandGetDefault(HandlerInputBase):
    """
    Command to get forecast for a default locality.
    """

    def _process(self):
        self._reply_with_forecast(Locality(self.user.default_locality_id))


class HandlerCommandSetDefault(HandlerInputBase):
    """
    Command to set latest locality as default.
    """

    def _process(self):
        self.user.default_locality_id, self.user.default_locality_name = (
            self.user.latest_locality_id,
            self.user.latest_locality_name,
        )
        self.reply(
            text=f"{self.user.default_locality_name} "
            f"{CONFIG['MESSAGES']['SET_DEFAULT_CONF']}",
            reply_markup=self._keyboard(),
        )
