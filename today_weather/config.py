import configparser
import os

import dotenv


dotenv.load_dotenv()
CONFIG = configparser.ConfigParser()
CONFIG.read("config.ini")

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")

# Database
if os.getenv("DATABASE_URL") is None:
    DATABASE_URI = (
        f"postgres+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PWD')}"
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
