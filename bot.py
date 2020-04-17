import logging
import os
from parser import get_today_weather

import telegram
from dotenv import load_dotenv
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from geocoding import geocode
from recommend import Recommender

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")
logging.basicConfig(level=logging.INFO)


bot = telegram.Bot(token=TELEGRAM_TOKEN)


def bot_reply(update, context, text):
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    logging.info(text)


def welcome(update, context):
    bot_reply(
        update,
        context,
        text="Введите город на любом языке (и опционально страну) для прогноза погоды на день",
    )


def get_weather(update, context):
    logging.info(f"{update.message.from_user.username} {update.message.text}")
    try:
        address, lat, lng = geocode(update.message.text)
    except IndexError:
        bot_reply(update, context, text="Не получилось найти такой город")
        return
    try:
        today_weather = get_today_weather(lat, lng)
    except Exception:
        bot_reply(update, context, text="Не получилось достать прогноз погоды")
        return
    text = Recommender(today_weather).recommend() + "-" * 30 + f"\n{address}"
    bot_reply(update, context, text=text)


def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", welcome))
    dispatcher.add_handler(MessageHandler(Filters.text, get_weather))
    updater.start_polling()


if __name__ == "__main__":
    main()
