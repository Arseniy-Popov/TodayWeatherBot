import logging

import click
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from today_weather.config import get_token
from today_weather.exceptions import custom_exception_handler
from today_weather.handlers import HandlerInput, HandlerWelcome


@click.command()
@click.option("--testing", default=False)
def main(testing=False):
    """
    Starts the bot up, adds handlers.
    """
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
    main()
