import logging
import os
from parser import get_today_weather

import telegram
from dotenv import load_dotenv
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from geocoding import geocode
from recommend import Recommender

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


bot = telegram.Bot(token=TELEGRAM_TOKEN)


def bot_reply(update, context, text):
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    print(text)


def get_weather(update, context):
    try:
        address, lat, lng = geocode(update.message.text)
    except IndexError:
        bot_reply(update, context, text="Не получилось найти такой город")
        return
    try:
        today_weather = get_today_weather(lat, lng)
    except Exception as e:
        bot_reply(update, context, text="Не получилось достать прогноз погоды")
        return
    text = Recommender(today_weather).recommend() + "-" * 30 + f"\n{address}"
    bot_reply(update, context, text=text)


def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    input_handler = MessageHandler(Filters.text, get_weather)
    dispatcher.add_handler(input_handler)
    # dispatcher.add_error_handler(error_callback)
    updater.start_polling()


if __name__ == "__main__":
    main()
