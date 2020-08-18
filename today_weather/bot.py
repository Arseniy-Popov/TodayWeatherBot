import logging
from abc import ABC, abstractmethod

from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from today_weather.config import CONFIG, TELEGRAM_TOKEN
from today_weather.db import get_user_attr, set_user_attr
from today_weather.db import Locality
from today_weather.utils.geocoding import AddressError, geocode
from today_weather.utils.owmparser import OWMParser
from today_weather.utils.recommend import Recommender


class HandlerBase(ABC):
    def __init__(self, update, context):
        self.update = update
        self.context = context
        self.process()

    @abstractmethod
    def process(self):
        pass

    def reply(self, **kwargs):
        self.update.message.reply_text(**kwargs)


class HandlerWelcome(HandlerBase):
    def process(self):
        self.reply(text=CONFIG["MESSAGES"]["WELCOME"])


class HandlerInput(HandlerBase):
    def process(self):
        user_message = self.update.message.text
        if user_message == CONFIG["KEYBOARD"]["REPEAT"]:
            self._reply_with_forecast(self.latest_locality)
        elif user_message == CONFIG["KEYBOARD"]["SET_DEFAULT"]:
            self.default_address = self.latest_locality
            self.reply(
                text=self.default_address + f" has been set as default",
                reply_markup=self._keyboard(),
            )
        elif CONFIG["KEYBOARD"]["GET_DEFAULT"] in user_message:
            self._reply_with_forecast(self.default_address)
        else:
            self._reply_with_forecast(user_message)

    def _reply_with_forecast(self, input):
        try:
            locality = (
                input if isinstance(input, Locality) else self._get_locality(input)
            )
            weather = self._get_weather(locality)
        except Exception:
            return
        text = Recommender(weather).recommend() + "-" * 30 + f"\n{locality.name}"
        self.reply(text=text, reply_markup=self._keyboard())
        self.latest_locality = locality

    def _get_locality(self, input):
        try:
            address, lat, lng = geocode(input)
            return Locality(address, lat, lng)
        except AddressError as e:
            self.reply(text=CONFIG["ERROR"]["GEOCODING_NOT_LOCALITY"])
            raise e
        except Exception as e:
            self.reply(text=CONFIG["ERROR"]["GEOCODING_GENERAL"])
            raise e

    def _get_weather(self, locality):
        try:
            today_weather = OWMParser().get_today_weather(locality.lat, locality.lng)
            return today_weather
        except Exception:
            self.reply(text=CONFIG["ERROR"]["OWM_GENERAL"])
            raise Exception

    def _keyboard(self):
        _keyboard = [
            [CONFIG["KEYBOARD"]["REPEAT"]],
            [CONFIG["KEYBOARD"]["SET_DEFAULT"]],
        ]
        if self.default_address is not None:
            _keyboard.append([f"Default: {self.default_address}"])
        return ReplyKeyboardMarkup(_keyboard, resize_keyboard=True)

    @property
    def default_locality(self):
        return get_user_attr(
            user_id=self.update.message.from_user.id, attr="default_locality"
        )

    @default_locality.setter
    def default_locality(self, locality):
        set_user_attr(
            user_id=self.update.message.from_user.id,
            attr="default_locality",
            value=locality,
        )

    @property
    def latest_locality(self):
        return get_user_attr(
            user_id=self.update.message.from_user.id, attr="latest_locality"
        )

    @latest_locality.setter
    def latest_locality(self, locality):
        set_user_attr(
            user_id=self.update.message.from_user.id,
            attr="latest_locality",
            value=locality,
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    handlers = [
        CommandHandler("start", HandlerWelcome),
        MessageHandler(Filters.text, HandlerInput),
    ]
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    for handler in handlers:
        dispatcher.add_handler(handler)
    updater.start_polling()
