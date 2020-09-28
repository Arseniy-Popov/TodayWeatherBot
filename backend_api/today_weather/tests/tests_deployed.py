"""
Test the deployed app.
"""


import requests

from today_weather.config import CONFIG

from .tests_integration import FORECAST_KEYS, LOCALITY_KEYS, assert_keys_match


URL = CONFIG["TESTS"]["URL_DEPLOYED"]


def test_get_locality():
    response = requests.get(URL + "/localities/1")
    response = response.json()
    assert_keys_match(response["locality"], LOCALITY_KEYS)


def test_get_locality_forecast():
    response = requests.get(URL + "/localities/1/forecast")
    response = response.json()
    assert_keys_match(response["forecast"], FORECAST_KEYS)
    assert_keys_match(response["locality"], LOCALITY_KEYS)


def test_post_address():
    response = requests.post(URL + "/localities", json={"address": "moscow"})
    response = response.json()
    assert_keys_match(response["forecast"], FORECAST_KEYS)
    assert_keys_match(response["locality"], LOCALITY_KEYS)
    assert "Moscow" in response["locality"]["name"]
