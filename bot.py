import os
import telegram
from recommend import Recommender
from telegram.ext import CommandHandler, Updater
from dotenv import load_dotenv
from parser import get_today_weather
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")


bot = telegram.Bot(token=TELEGRAM_TOKEN)


def reply_to_command(update, context, text):
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    print(text)


def get_weather(update, context):
    text = Recommender(get_today_weather()).recommend()
    reply_to_command(update, context, text=text)


def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("weather", get_weather))
    updater.start_polling()


if __name__ == "__main__":
    main()