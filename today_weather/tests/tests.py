import unittest

from pyrogram import Client, MessageHandler

from today_weather.config import TELEGRAM_APP_API_HASH, TELEGRAM_APP_API_ID, CONFIG


class Empty:
    pass


class TestTodayWeather(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bot = CONFIG["BOTS"]["TEST_BOT_USERNAME"]
        cls.app = Client(
            "today_weather", api_id=TELEGRAM_APP_API_ID, api_hash=TELEGRAM_APP_API_HASH
        )
        cls.app.start()
        cls.last_response = None, None

    @classmethod
    def tearDownClass(cls):
        cls.app.stop()

    def setUp(self):
        def register_response(client, message):
            self.response = message

        self.register_response_handler = MessageHandler(register_response)
        self.app.add_handler(self.register_response_handler)
        self.response = Empty

    def tearDown(self):
        self.app.remove_handler(self.register_response_handler)

    def _await_response(self):
        while self.response == Empty or self.response == self.__class__.last_response:
            pass
        self.__class__.last_response = self.response

    def _assertKeyboardContains(self, response, *messages):
        return all(
            [message] in response.reply_markup["keyboard"] for message in messages
        )

    def test_welcome(self):
        self.app.send_message(self.bot, "/start")
        self._await_response()
        self.assertEqual(self.response.text, CONFIG["MESSAGES"]["WELCOME"])

    def test_address(self, address="New York"):
        self.app.send_message(self.bot, address)
        self._await_response()
        self.assertEqual("\u00B0C" in self.response.text, True)
        self.assertEqual(address in self.response.text, True)
        self._assertKeyboardContains(
            self.response,
            CONFIG["KEYBOARD"]["SET_DEFAULT"],
            CONFIG["KEYBOARD"]["SET_DEFAULT"],
        )

    def test_address_wrong(self):
        with self.subTest("narrow"):
            self.app.send_message(self.bot, "Times Square")
            self._await_response()
            self.assertEqual(
                self.response.text, CONFIG["ERROR"]["GEOCODING_NOT_LOCALITY"]
            )
        with self.subTest("wide"):
            self.app.send_message(self.bot, "USA")
            self._await_response()
            self.assertEqual(
                self.response.text, CONFIG["ERROR"]["GEOCODING_NOT_LOCALITY"]
            )

    def test_repeat(self):
        self.test_address()
        self.app.send_message(self.bot, CONFIG["KEYBOARD"]["REPEAT"])
        self._await_response()
        self.assertEqual("\u00B0C" in self.response.text, True)
        self.assertEqual("New York" in self.response.text, True)

    def test_set_default(self):
        self.test_address("Moscow")
        self.app.send_message(self.bot, CONFIG["KEYBOARD"]["SET_DEFAULT"])
        self._await_response()
        self.assertEqual(
            CONFIG["MESSAGES"]["SET_DEFAULT_CONF"] in self.response.text, True
        )

    # def test_get_default(self):
    #     self.test_set_default()
    #     self.app.send_message(self.bot, CONFIG["KEYBOARD"]["SET_DEFAULT"])


if __name__ == "__main__":
    unittest.main()
