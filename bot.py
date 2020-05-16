import configparser
import logging
import os

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

from geocoding import geocode
from owmparser import OWMParser
from recommend import Recommender


TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")
logging.basicConfig(level=logging.INFO)
config = configparser.ConfigParser()
config.read("config.ini")


def welcome_handler(update, context):
    update.message.reply_text(config["MESSAGES"]["WELCOME"])


def keyboard(update, context):
    default_address = context.user_data.get("default_address", None)
    keyboard = [["Repeat"], ["Set as default address"]]
    if default_address is not None:
        keyboard.append([f"Default: {default_address}"])
    else:
        keyboard.append([f"Default: set it first"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_weather(update, context, message):
    try:
        address, lat, lng = geocode(message.text)
    except AttributeError:
        address, lat, lng = geocode(message)
    except IndexError:
        message.reply_text(text=config["ERROR"]["GEOCODING"])
        return
    try:
        today_weather = OWMParser().get_today_weather(lat, lng)
    except Exception:
        message.reply_text(text=config["ERROR"]["OWM_REQUEST"])
        raise Exception
    text = Recommender(today_weather).recommend() + "-" * 30 + f"\n{address}"
    update.message.reply_text(text=text, reply_markup=keyboard(update, context))
    context.user_data["latest_address"] = address


def input_handler(update, context):
    if update.message.text == "Repeat":
        get_weather(update, context, message=context.user_data["latest_address"])
    elif update.message.text == "Set as default address":
        context.user_data["default_address"] = context.user_data["latest_address"]
        update.message.reply_text(text=f"Set {context.user_data['default_address']} as default", reply_markup=keyboard(update, context))
    elif "Default" in update.message.text:
        get_weather(update, context, message=context.user_data["default_address"])
    else:
        get_weather(update, context, message=update.message)


def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", welcome_handler))
    dispatcher.add_handler(MessageHandler(Filters.text, input_handler))
    updater.start_polling()


if __name__ == "__main__":
    main()
