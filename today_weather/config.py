import configparser
import os
import dotenv


dotenv.load_dotenv()
CONFIG = configparser.ConfigParser()
CONFIG.read("config.ini")

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")

# Database
DATABASE_URI = (
    f"postgres+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PWD')}"
    f"@localhost:5432/{CONFIG['DB']['DB_TABLENAME']}"
)

# Google Maps Geocoding API
GOOG_MAPS_API_KEY = os.environ["GOOG_MAPS_API_KEY"]

# Open Weather Map API
OWM_API_KEY = os.environ["OWM_API_KEY"]