import unittest

from pyrogram import Client

from today_weather.config import TELEGRAM_APP_API_HASH, TELEGRAM_APP_API_ID, CONFIG


class Empty:
    pass


class TestTodayWeather(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bot = CONFIG["BOTS"]["TEST_BOT_USERNAME"]
        cls.app = Client(
            "today_weather",
            api_id=TELEGRAM_APP_API_ID,
            api_hash=TELEGRAM_APP_API_HASH
        )
        cls.app.start()
        @cls.app.on_message()
        def register_response(client, message):
            cls.response = message

    @classmethod
    def tearDownClass(cls):
        cls.app.stop()
    
    def setUp(self):
        self.__class__.response = Empty
    
    # def tearDown(self):
    #     self.app.remove_handler
    
    def _await_response(self):
        while self.__class__.response == Empty:
            pass
    
    def test_welcome(self):
        self.app.send_message(self.bot, "/start")
        self._await_response()
        self.assertEqual(self.response.text, CONFIG["MESSAGES"]["WELCOME"])        

    def test_address(self):
        self.app.send_message(self.bot, "New York")
        self._await_response()
        self.assertEqual("\u00B0C" in self.response.text, True)
        self.assertEqual("New York" in self.response.text, True)


if __name__ == "__main__":
    unittest.main()