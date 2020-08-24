import configparser
import os

import dotenv


TEST_DB = False
TEST_DEPLOYED = True
dotenv.load_dotenv()
CONFIG = configparser.ConfigParser()
CONFIG.read("config.ini")

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")

# Database
if TEST_DB:
    DATABASE_URI = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PWD')}"
        f"@localhost:5432/{CONFIG['DB']['DB_NAME_TEST']}"
    )
elif os.getenv("DATABASE_URL") is None:
    DATABASE_URI = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PWD')}"
        f"@localhost:5432/{CONFIG['DB']['DB_NAME']}"
    )
else:
    DATABASE_URI = os.getenv("DATABASE_URL")

# Google Maps Geocoding API
GOOG_MAPS_API_KEY = os.environ["GOOG_MAPS_API_KEY"]

# Open Weather Map API
OWM_API_KEY = os.environ["OWM_API_KEY"]

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
