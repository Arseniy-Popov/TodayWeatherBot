import configparser
import os


# general
CONFIG = configparser.ConfigParser()
CONFIG.read("config.ini")

# bot
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")

# database
DATABASE_URI = (
    f"postgres+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PWD')}"
    f"@localhost:5432/{CONFIG['DB']['DB_TABLENAME']}"
)
