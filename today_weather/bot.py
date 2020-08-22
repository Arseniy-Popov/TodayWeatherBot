import logging

from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from today_weather.handlers import HandlerWelcome, HandlerInput
from today_weather.config import TELEGRAM_TOKEN


def main():
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
