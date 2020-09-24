import argparse
import logging

from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from today_weather.config import get_token
from today_weather.handlers import HandlerInput, HandlerWelcome
from today_weather.exceptions import custom_exception_handler


def main(testing=False):
    logging.basicConfig(level=logging.INFO)
    updater = Updater(get_token(testing), use_context=True)
    dispatcher = updater.dispatcher
    handlers = [
        CommandHandler("start", HandlerWelcome),
        MessageHandler(Filters.text, HandlerInput),
    ]
    for handler in handlers:
        dispatcher.add_handler(handler)
    error_handlers = [custom_exception_handler]
    for handler in error_handlers:
        dispatcher.add_error_handler(handler)
    updater.start_polling()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--testing", default=False)
    main(testing=parser.parse_args())
