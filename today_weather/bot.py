import logging
from abc import ABC, abstractmethod

from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

import config
from config import CONFIG
from utils.geocoding import geocode, AddressError
from utils.owmparser import OWMParser
from utils.recommend import Recommender
from db import get_user_attr, set_user_attr


logging.basicConfig(level=logging.INFO)


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
        if user_message == "Repeat":
            self.reply_forecast(self.latest_address)
        elif user_message == "Set as default address":
            self.default_address = self.latest_address
            self.reply(
                text=f"Set {self.default_address} as default",
                reply_markup=self.keyboard(),
            )
        elif "Default" in user_message:
            self.reply_forecast(self.default_address)
        else:
            self.reply_forecast(user_message)

    def reply_forecast(self, text):
        address, lat, lng = self.get_address(text)
        weather = self.get_weather(lat, lng)
        text = Recommender(weather).recommend() + "-" * 30 + f"\n{address}"
        self.reply(text=text, reply_markup=self.keyboard())
        self.latest_address = address

    def get_address(self, text):
        try:
            address, lat, lng = geocode(text)
        except AddressError:
            self.reply(text=CONFIG["ERROR"]["GEOCODING_NOT_LOCALITY"])
            return
        except Exception:
            self.reply(text=CONFIG["ERROR"]["GEOCODING_GENERAL"])
            return
        return address, lat, lng

    def get_weather(self, lat, lng):
        try:
            today_weather = OWMParser().get_today_weather(lat, lng)
        except Exception:
            self.reply(text=CONFIG["ERROR"]["OWM_GENERAL"])
            raise Exception
        return today_weather

    def keyboard(self):
        keyboard = [["Repeat"], ["Set as default address"]]
        if self.default_address is not None:
            keyboard.append([f"Default: {self.default_address}"])
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @property
    def default_address(self):
        return get_user_attr(
            user_id=self.update.message.from_user.id, attr="default_address"
        )

    @default_address.setter
    def default_address(self, address):
        set_user_attr(
            user_id=self.update.message.from_user.id,
            attr="default_address",
            value=address,
        )

    @property
    def latest_address(self):
        return get_user_attr(
            user_id=self.update.message.from_user.id, attr="latest_address"
        )

    @latest_address.setter
    def latest_address(self, address):
        set_user_attr(
            user_id=self.update.message.from_user.id,
            attr="latest_address",
            value=address,
        )


if __name__ == "__main__":
    handlers = [
        CommandHandler("start", HandlerWelcome),
        MessageHandler(Filters.text, HandlerInput),
    ]
    updater = Updater(config.TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    for handler in handlers:
        dispatcher.add_handler(handler)
    updater.start_polling()
