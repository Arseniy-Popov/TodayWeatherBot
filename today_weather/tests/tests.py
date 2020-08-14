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

    @classmethod
    def tearDownClass(cls):
        cls.app.stop()
    
    def setUp(self):
        self.response = Empty
        @self.app.on_message()
        def register_response(client, message):
            self.response = message
    
    def _await_response(self):
        while self.response == Empty:
            pass
    
    def test_welcome(self):
        self.app.send_message(self.bot, "/start")
        self._await_response()
        self.assertEqual(self.response.text, CONFIG["MESSAGES"]["WELCOME"])        


if __name__ == "__main__":
    unittest.main()