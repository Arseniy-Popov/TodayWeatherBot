import configparser
import logging
import os

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
    CallbackQueryHandler,
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
    default_city = context.user_data.get("default_city", None)
    keyboard = [
        ["Repeat"],
        ["Set as default city"],
    ]
    if default_city is not None:
        keyboard.append([f"Default: {default_city.text}"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_weather(update, context, message):
    logging.info(f"{message.from_user.username} {message.text}")
    try:
        address, lat, lng = geocode(message.text)
    except IndexError:
        message.reply_text(text=config["ERROR"]["GEOCODING"])
        return
    try:
        today_weather = OWMParser().get_today_weather(lat, lng)
    except Exception:
        message.reply_text(text=config["ERROR"]["OWM_REQUEST"])
        raise Exception
    text = Recommender(today_weather).recommend() + "-" * 30 + f"\n{address}"
    message.reply_text(
        text=text, reply_markup=keyboard(update, context)
    )
    context.user_data["latest_message"] = message
    

def input_handler(update, context):
    default_city = context.user_data.get("default_city", None)
    if update.message.text == "Repeat":
        get_weather(update, context, message=context.user_data["latest_message"])
    elif update.message.text == "Set as default city":
        context.user_data["default_city"] = update.message    
    elif "Default" in update.message.text:
        get_weather(update, context, message=context.user_data["default_city"])
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
