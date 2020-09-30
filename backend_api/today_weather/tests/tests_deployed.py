"""
Test the deployed app.
"""


import pytest
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


@pytest.mark.parametrize(
    "address",
    [
        "Moscow",
        "Berlin",
        "Warsaw",
        "Berlin",
        "Amsterdam",
        "Paris",
        "London",
        "Lisbon",
        "Toronto",
    ],
)
def test_post_address(address):
    response = requests.post(URL + "/localities", json={"address": address})
    assert response.status_code in (200, 201)
    response = response.json()
    assert_keys_match(response["forecast"], FORECAST_KEYS)
    assert_keys_match(response["locality"], LOCALITY_KEYS)
    assert address in response["locality"]["name"]
