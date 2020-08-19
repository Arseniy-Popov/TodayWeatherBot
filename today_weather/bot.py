import logging
from abc import ABC, abstractmethod

from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from today_weather.config import CONFIG, TELEGRAM_TOKEN
from today_weather.db import get_user_attr, set_user_attr, write_to_db
from today_weather.models import AddressInput, Locality
from today_weather.utils.misc import log_reply
from today_weather.utils.geocoding import AddressError, geocode
from today_weather.utils.owmparser import OWMParser
from today_weather.utils.recommend import Recommender


class HandlerBase(ABC):
    def __init__(self, update, context):
        self.update = update
        self.context = context
        self.user_id = self.update.message.from_user.id
        self.user_message_text = self.update.message.text
        self.process()

    @abstractmethod
    def process(self):
        pass

    def reply(self, **kwargs):
        self.update.message.reply_text(**kwargs)
        log_reply(self.user_id, kwargs)


class HandlerWelcome(HandlerBase):
    def process(self):
        self.reply(text=CONFIG["MESSAGES"]["WELCOME"])


class HandlerInput(HandlerBase):
    def process(self):
        logging.info(f"message from {self.user_id}: {self.user_message_text}")
        if self.user_message_text == CONFIG["KEYBOARD"]["REPEAT"]:
            self._reply_with_forecast(self.latest_locality)
        elif self.user_message_text == CONFIG["KEYBOARD"]["SET_DEFAULT"]:
            self.default_locality = self.latest_locality
            self.reply(
                text=f"{self.default_locality.name} {CONFIG['MESSAGES']['SET_DEFAULT_CONF']}",
                reply_markup=self._keyboard(),
            )
        elif CONFIG["KEYBOARD"]["GET_DEFAULT"] in self.user_message_text:
            self._reply_with_forecast(self.default_locality)
        else:
            self._reply_with_forecast(self.user_message_text)

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
        except AddressError as e:
            self.reply(text=CONFIG["ERROR"]["GEOCODING_NOT_LOCALITY"])
            raise e
        except Exception as e:
            self.reply(text=CONFIG["ERROR"]["GEOCODING_GENERAL"])
            raise e
        locality = Locality(name=address, lat=lat, lng=lng) #get or create
        write_to_db(AddressInput(input=input, locality=locality)) #get or create
        return locality

    def _get_weather(self, locality):
        try:
            today_weather = OWMParser().get_today_weather(locality.lat, locality.lng)
            return today_weather
        except Exception as e:
            self.reply(text=CONFIG["ERROR"]["OWM_GENERAL"])
            raise e

    def _keyboard(self):
        _keyboard = [
            [CONFIG["KEYBOARD"]["REPEAT"]],
            [CONFIG["KEYBOARD"]["SET_DEFAULT"]],
        ]
        if self.default_locality is not None:
            _keyboard.append([f"Default: {self.default_locality}"])
        return ReplyKeyboardMarkup(_keyboard, resize_keyboard=True)

    @property
    def default_locality(self):
        return get_user_attr(
            user_id=self.user_id, attr="default_locality"
        )

    @default_locality.setter
    def default_locality(self, locality):
        set_user_attr(
            user_id=self.user_id,
            attr="default_locality",
            value=locality,
        )

    @property
    def latest_locality(self):
        return get_user_attr(
            user_id=self.user_id, attr="latest_locality"
        )

    @latest_locality.setter
    def latest_locality(self, locality):
        set_user_attr(
            user_id=self.user_id,
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
