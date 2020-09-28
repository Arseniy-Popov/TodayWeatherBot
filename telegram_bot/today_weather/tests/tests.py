import os
import shlex
import subprocess
import unittest

from pyrogram import Client, Filters, MessageHandler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from today_weather.config import (
    CONFIG,
    DATABASE_URI,
    TELEGRAM_APP_API_HASH,
    TELEGRAM_APP_API_ID,
    TEST_DB,
    TEST_DEPLOYED,
    USERNAME_BOT_TO_TEST,
)
from today_weather.models import Base


class Empty:
    pass


class TestTodayWeather(unittest.TestCase):

    # Class-level set-up and tear-down -------------------------------------------------

    @classmethod
    def setUpClass(cls):
        cls.bot = USERNAME_BOT_TO_TEST
        # launch test TG client
        cls.app = Client(
            "today_weather", api_id=TELEGRAM_APP_API_ID, api_hash=TELEGRAM_APP_API_HASH
        )
        cls.app.start()
        # DB
        if TEST_DB:
            cls.engine = create_engine(DATABASE_URI)
            cls.Session = sessionmaker(bind=cls.engine)
            cls.session = cls.Session()

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
        if not TEST_DEPLOYED:
            self.subprocess = subprocess.Popen(
                shlex.split("pipenv run python -m today_weather.bot --testing True"),
                cwd=os.getcwd(),
                preexec_fn=os.setsid,
            )

    def tearDown(self):
        """
        Kills the bot and drops all tables in the test database.
        """
        self.app.remove_handler(self.register_response_handler)
        # kill the bot
        if not TEST_DEPLOYED:
            self.subprocess.kill()
            self.subprocess.wait()
        # drop tables
        if TEST_DB:
            Base.metadata.drop_all(self.engine)

    # Utilities ------------------------------------------------------------------------

    def _send_message(self, message):
        self.app.send_message(self.bot, message)

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
        self._send_message("/start")
        self._await_response()
        self.assertEqual(self.response.text, CONFIG["MESSAGES"]["WELCOME"])

    def test_address(self, address="New York"):
        self.address = address
        self._send_message(address)
        self._await_response()
        self._assertResponseContains("\u00B0C", self.address)
        self._assertKeyboardContains(
            CONFIG["KEYBOARD"]["SET_DEFAULT"], CONFIG["KEYBOARD"]["SET_DEFAULT"]
        )

    def test_address_wrong(self):
        with self.subTest("narrow"):
            self._send_message("Times Square")
            self._await_response()
            self._assertResponseContains("too general or too narrow")
        with self.subTest("wide"):
            self._send_message("USA")
            self._await_response()
            self._assertResponseContains("too general or too narrow")

    def test_repeat(self):
        self.test_address()
        self._send_message(CONFIG["KEYBOARD"]["REPEAT"])
        self._await_response()
        self._assertResponseContains("\u00B0C", self.address)

    def test_set_default(self, address="Moscow"):
        self.default_address = address
        self.test_address(self.default_address)
        self._send_message(CONFIG["KEYBOARD"]["SET_DEFAULT"])
        self._await_response()
        self._assertResponseEquals(CONFIG["MESSAGES"]["SET_DEFAULT_CONF"])

    def test_get_default(self):
        self.test_set_default()
        self.test_address()
        self._send_message(CONFIG["KEYBOARD"]["GET_DEFAULT"])
        self._await_response()
        self._assertResponseContains("\u00B0C", self.default_address)

        
if __name__ == "__main__":
    unittest.main(verbosity=2)
