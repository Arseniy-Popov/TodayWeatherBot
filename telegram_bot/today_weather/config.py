import configparser
import os

import dotenv

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
else:
    DATABASE_URI = (
        f"postgresql+psycopg2://arseniypopov:{os.getenv('POSTGRES_PASSWORD')}"
        f"@localhost:5432/{CONFIG['DB']['DB_NAME']}"
    )

# # Testing
# try:
#     TELEGRAM_APP_API_ID = os.environ["TELEGRAM_APP_API_ID"]
#     TELEGRAM_APP_API_HASH = os.environ["TELEGRAM_APP_API_HASH"]
# except:
#     pass
# if TEST_DEPLOYED:
#     USERNAME_BOT_TO_TEST = CONFIG["BOTS"]["BOT_USERNAME"]
# else:
#     USERNAME_BOT_TO_TEST = CONFIG["BOTS"]["TEST_BOT_USERNAME"]
