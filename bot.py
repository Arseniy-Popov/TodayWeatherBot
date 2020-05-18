import configparser
import logging
import os
from abc import ABC, abstractmethod

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from geocoding import geocode
from owmparser import OWMParser
from recommend import Recommender


TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")
logging.basicConfig(level=logging.INFO)
CONFIG = configparser.ConfigParser()
CONFIG.read("config.ini")


class BaseHandler(ABC):
    def __init__(self, update, context):
        self.update = update
        self.context = context
        self.process()

    @abstractmethod
    def process(self):
        pass

    def reply(self, **kwargs):
        self.update.message.reply_text(**kwargs)


class HandlerWelcome(BaseHandler):
    def process(self):
        self.reply(text=CONFIG["MESSAGES"]["WELCOME"])


class HandlerInput(BaseHandler):
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
        except IndexError:
            self.reply(text=CONFIG["ERROR"]["GEOCODING"])
            return
        return address, lat, lng

    def get_weather(self, lat, lng):
        try:
            today_weather = OWMParser().get_today_weather(lat, lng)
        except Exception:
            self.reply(text=CONFIG["ERROR"]["OWM_REQUEST"])
            raise Exception
        return today_weather

    def keyboard(self):
        keyboard = [["Repeat"], ["Set as default address"]]
        if self.default_address is not None:
            keyboard.append([f"Default: {self.default_address}"])
        else:
            keyboard.append([f"Default: set it first"])
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @property
    def default_address(self):
        return self.context.user_data.get("default_address", None)

    @default_address.setter
    def default_address(self, address):
        self.context.user_data["default_address"] = address

    @property
    def latest_address(self):
        return self.context.user_data.get("latest_address", None)

    @latest_address.setter
    def latest_address(self, address):
        self.context.user_data["latest_address"] = address


if __name__ == "__main__":
    handlers = [
        CommandHandler("start", HandlerWelcome),
        MessageHandler(Filters.text, HandlerInput),
    ]
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    for handler in handlers:
        dispatcher.add_handler(handler)
    updater.start_polling()
