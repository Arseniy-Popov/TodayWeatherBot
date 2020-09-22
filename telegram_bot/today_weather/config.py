import configparser
import os

import dotenv

dotenv.load_dotenv()
CONFIG = configparser.ConfigParser()
CONFIG.read("config.ini")

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")

# Testing
try:
    TELEGRAM_APP_API_ID = os.environ["TELEGRAM_APP_API_ID"]
    TELEGRAM_APP_API_HASH = os.environ["TELEGRAM_APP_API_HASH"]
except:
    pass
if TEST_DEPLOYED:
    USERNAME_BOT_TO_TEST = CONFIG["BOTS"]["BOT_USERNAME"]
else:
    USERNAME_BOT_TO_TEST = CONFIG["BOTS"]["TEST_BOT_USERNAME"]
