from unittest.mock import patch

import pytest
from sqlalchemy.orm.session import close_all_sessions

from today_weather.app import init_app, init_db, make_app
from today_weather.config import CONFIG
from today_weather.models import Base


# Fixtures -----------------------------------------------------------------------------


FORECAST_KEYS = ["rain", "snow", "temp_min", "temp_max"]
LOCALITY_KEYS = ["lat", "lng", "name", "links"]


@pytest.fixture
def app():
    app = make_app(testing=True)
    # drop db before each test
    drop_db(app)
    app = init_app(app)
    yield app


@pytest.fixture
def client(app):
    yield app.test_client()


@pytest.fixture
def pre_post_localities(client):
    client.post("/localities", json={"address": "москва"})
    client.post("/localities", json={"address": "new york"})


# Utilities ----------------------------------------------------------------------------


def drop_db(app):
    session, engine = init_db(app)
    close_all_sessions()
    Base.metadata.drop_all(engine)


def assert_keys_match(obj, keys):
    assert len(obj) == len(keys)
    for key in keys:
        assert key in obj


# POST /localities ---------------------------------------------------------------------


def test_post_address(client, address="москва", expected="Moscow", order=1):
    response = client.post("/localities", json={"address": address})
    assert response.status_code == 201
    response = response.get_json()
    assert_keys_match(response["forecast"], FORECAST_KEYS)
    assert_keys_match(response["locality"], LOCALITY_KEYS)
    assert expected in response["locality"]["name"]
    assert f"/localities/{order}" == response["locality"]["links"]["self"]


def test_post_address_cached(client, monkeypatch):
    client.post("/localities", json={"address": "москва"})
    with patch("today_weather.views.geocode") as geocode:
        response = client.post("/localities", json={"address": "москва"})
        geocode.assert_not_called()
        assert response.status_code == 200


def test_post_address_multiple(client):
    test_post_address(client)
    test_post_address(client, address="new york", expected="New York", order=2)


# GET /localities/<id> -----------------------------------------------------------------


@pytest.mark.parametrize(
    "url, locality", [("/localities/1", "Moscow"), ("/localities/2", "New York")]
)
def test_get_locality(client, pre_post_localities, url, locality):
    response = client.get(url)
    assert response.status_code == 200
    response = response.get_json()
    assert_keys_match(response["locality"], LOCALITY_KEYS)
    assert locality in response["locality"]["name"]


# GET /localities/<id>/forecast --------------------------------------------------------


@pytest.mark.parametrize(
    "url, locality", [("/localities/1", "Moscow"), ("/localities/2", "New York")]
)
def test_get_locality_forecast(client, pre_post_localities, url, locality):
    response = client.get(url + "/forecast")
    assert response.status_code == 200
    response = response.get_json()
    assert_keys_match(response["locality"], LOCALITY_KEYS)
    assert_keys_match(response["forecast"], FORECAST_KEYS)
    assert locality in response["locality"]["name"]


# Other --------------------------------------------------------------------------------


def test_errors(client):
    response = client.get("/localities/1")
    assert response.status_code == 404
    response = client.post("/localities", json={"address": "russia"})
    assert response.status_code == 400
    assert response.get_json()["error"] == CONFIG["ERROR"]["GEOCODING_NOT_LOCALITY"]
    response = client.get("/localities/1/forecast")
    assert response.status_code == 404
