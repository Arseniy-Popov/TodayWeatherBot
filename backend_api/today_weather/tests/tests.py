import pytest

from today_weather import app
from today_weather.router import init_app

FORECAST_KEYS = ["rain", "snow", "temp_min", "temp_max"]
LOCALITY_KEYS = ["lat", "lng", "name", "links"]


@pytest.fixture
def client():
    app.config["TESTING"] = True
    client = init_app(app)
    yield client.test_client()


def assert_keys_match(obj, keys):
    assert len(obj) == len(keys)
    for key in keys:
        assert key in obj


def test_post_address(client, address="москва"):
    response = client.post("/localities", json={"address": address})
    assert response.status_code == 201
    response = response.get_json()
    assert_keys_match(response["forecast"], FORECAST_KEYS)
    assert_keys_match(response["locality"], LOCALITY_KEYS)
    assert "Moscow" in response["locality"]["name"]


def test_post_address_cached(client):
    test_post_address(client)
    response = client.post("/localities", json={"address": "москва"})
    assert response.status_code == 201


@pytest.mark.parametrize(
    "url, locality", [("/localities/1", "Moscow"), ("/localities/2", "New York")]
)
def test_get_address(client, url, locality):
    test_post_address(client)
    test_post_address(client, address="new york")
    response = client.get(url)
    assert response.status_code == 200
    response = response.get_json()
    assert_keys_match(response["locality"], LOCALITY_KEYS)
    assert locality in response["locality"]["name"]
