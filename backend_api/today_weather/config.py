import configparser
import os

import dotenv

from today_weather import app

dotenv.load_dotenv()
CONFIG = configparser.ConfigParser()
CONFIG.read("config.ini")


# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")

# Database
if os.getenv("DOCKER"):
    DATABASE_URI = (
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
elif app.config["TESTING"]:
    DATABASE_URI = (
        f"postgresql+psycopg2://arseniypopov:{os.getenv('POSTGRES_PASSWORD')}"
        f"@localhost:5432/{CONFIG['DB']['DB_NAME_TEST']}"
    )
else:
    DATABASE_URI = (
        f"postgresql+psycopg2://arseniypopov:{os.getenv('POSTGRES_PASSWORD')}"
        f"@localhost:5432/{CONFIG['DB']['DB_NAME']}"
    )

# Google Maps Geocoding API
GOOG_MAPS_API_KEY = os.environ["GOOG_MAPS_API_KEY"]

# Open Weather Map API
OWM_API_KEY = os.environ["OWM_API_KEY"]
