import configparser
import os

import dotenv

dotenv.load_dotenv()
CONFIG = configparser.ConfigParser()
CONFIG.read("config.ini")

TEST_DB = True
TEST_DEPLOYED = True

# Telegram -----------------------------------------------------------------------------


def get_token(testing):
    if testing == "False":
        return os.getenv("TELEGRAM_BOT_API_TOKEN")
    return os.getenv("TELEGRAM_BOT_API_TOKEN_TEST")


# Database -----------------------------------------------------------------------------

if os.getenv("DATABASE_URL") is not None:
    DATABASE_URI = os.getenv("DATABASE_URL")
elif not TEST_DB:
    DATABASE_URI = (
        f"postgresql+psycopg2://arseniypopov:{os.getenv('POSTGRES_PASSWORD')}"
        f"@localhost:5432/{CONFIG['DB']['DB_NAME_LOCAL']}"
    )
else:
    DATABASE_URI = (
        f"postgresql+psycopg2://arseniypopov:{os.getenv('POSTGRES_PASSWORD')}"
        f"@localhost:5432/{CONFIG['DB']['DB_NAME_TEST_LOCAL']}"
    )

# Testing ------------------------------------------------------------------------------

try:
    TELEGRAM_APP_API_ID = os.environ["TELEGRAM_APP_API_ID"]
    TELEGRAM_APP_API_HASH = os.environ["TELEGRAM_APP_API_HASH"]
except:
    pass
if TEST_DEPLOYED:
    USERNAME_BOT_TO_TEST = CONFIG["BOTS"]["BOT_USERNAME"]
else:
    USERNAME_BOT_TO_TEST = CONFIG["BOTS"]["BOT_USERNAME_TEST"]
