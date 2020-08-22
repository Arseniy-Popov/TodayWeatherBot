import os
import shlex
import subprocess
import unittest

import psutil
from pyrogram import Client, MessageHandler, Filters
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from today_weather.config import (
    CONFIG,
    TELEGRAM_APP_API_HASH,
    TELEGRAM_APP_API_ID,
    DATABASE_URI,
    USERNAME_BOT_TO_TEST
)
from today_weather.models import Base


class Empty:
    pass


class TestTodayWeather(unittest.TestCase):

    # Class-level set-up and tear-down -------------------------------------------------

    @classmethod
    def setUpClass(cls):
        cls.bot = USERNAME_BOT_TO_TEST
        cls.app = Client(
            "today_weather", api_id=TELEGRAM_APP_API_ID, api_hash=TELEGRAM_APP_API_HASH
        )
        cls.app.start()

    @classmethod
    def tearDownClass(cls):
        cls.app.stop()

    # Method-level set-up and tear-down ------------------------------------------------

    def setUp(self):
        """
        Adds a message handler to save the responses from the bot and restarts the bot
        between each test to test for data persistence. 
        """

        # add handler to register bot's response
        def register_response(client, message):
            """
            Saves the response from the bot.
            """
            self.response = message

        self.register_response_handler = MessageHandler(
            register_response, filters=Filters.user(self.bot)
        )
        self.app.add_handler(self.register_response_handler)
        self.response, self.last_response = Empty, Empty
        # restart the bot
        self.subprocess = subprocess.Popen(
            shlex.split("pipenv run python -m today_weather"),
            cwd=os.getcwd(),
            preexec_fn=os.setsid,
        )

    def tearDown(self):
        """
        Kills the bot and drops all tables in the test database.
        """
        # kill the bot
        self.app.remove_handler(self.register_response_handler)
        self.subprocess.kill()
        self.subprocess.wait()
        # drop tables
        engine = create_engine(DATABASE_URI)
        Session = sessionmaker(bind=engine)
        session = Session()
        Base.metadata.drop_all(engine)

    # Utilities ------------------------------------------------------------------------

    def _await_response(self):
        while self.response == Empty or self.response == self.last_response:
            pass
        self.last_response = self.response

    def _assertResponseContains(self, *items):
        return all(item in self.response.text for item in items)

    def _assertResponseEquals(self, item):
        return self.response.text == item

    def _assertKeyboardContains(self, *messages):
        return all(
            [message] in self.response.reply_markup["keyboard"] for message in messages
        )

    # Tests ----------------------------------------------------------------------------

    def test_welcome(self):
        self.app.send_message(self.bot, "/start")
        self._await_response()
        self.assertEqual(self.response.text, CONFIG["MESSAGES"]["WELCOME"])

    def test_address(self, address="New York"):
        self.address = address
        self.app.send_message(self.bot, address)
        self._await_response()
        self._assertResponseContains("\u00B0C", self.address)
        self._assertKeyboardContains(
            CONFIG["KEYBOARD"]["SET_DEFAULT"], CONFIG["KEYBOARD"]["SET_DEFAULT"]
        )

    def test_address_wrong(self):
        with self.subTest("narrow"):
            self.app.send_message(self.bot, "Times Square")
            self._await_response()
            self._assertResponseEquals(CONFIG["ERROR"]["GEOCODING_NOT_LOCALITY"])
        with self.subTest("wide"):
            self.app.send_message(self.bot, "USA")
            self._await_response()
            self._assertResponseEquals(CONFIG["ERROR"]["GEOCODING_NOT_LOCALITY"])

    def test_repeat(self):
        self.test_address()
        self.app.send_message(self.bot, CONFIG["KEYBOARD"]["REPEAT"])
        self._await_response()
        self._assertResponseContains("\u00B0C", self.address)

    def test_set_default(self, address="Moscow"):
        self.default_address = address
        self.test_address(self.default_address)
        self.app.send_message(self.bot, CONFIG["KEYBOARD"]["SET_DEFAULT"])
        self._await_response()
        self._assertResponseEquals(CONFIG["MESSAGES"]["SET_DEFAULT_CONF"])

    def test_get_default(self):
        self.test_set_default()
        self.test_address()
        self.app.send_message(self.bot, CONFIG["KEYBOARD"]["GET_DEFAULT"])
        self._await_response()
        self._assertResponseContains("\u00B0C", self.default_address)


if __name__ == "__main__":
    unittest.main()
