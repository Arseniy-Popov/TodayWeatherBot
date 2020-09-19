import pytest
from sqlalchemy.orm.session import close_all_sessions

from today_weather.app import make_app, init_app, init_db, drop_db


FORECAST_KEYS = ["rain", "snow", "temp_min", "temp_max"]
LOCALITY_KEYS = ["lat", "lng", "name", "links"]


@pytest.fixture
def app():
    app = make_app(testing=True)
    session, engine = init_db(app)
    close_all_sessions()
    drop_db(engine)
    app = init_app(app)
    yield app


@pytest.fixture
def client(app):
    yield app.test_client()


@pytest.fixture
def prepopulate_localities(client):
    

def assert_keys_match(obj, keys):
    assert len(obj) == len(keys)
    for key in keys:
        assert key in obj


def test_post_address(client, address="москва", expected="Moscow"):
    response = client.post("/localities", json={"address": address})
    assert response.status_code == 201
    response = response.get_json()
    assert_keys_match(response["forecast"], FORECAST_KEYS)
    assert_keys_match(response["locality"], LOCALITY_KEYS)
    assert expected in response["locality"]["name"]


def test_post_address_cached(client):
    test_post_address(client)
    response = client.post("/localities", json={"address": "москва"})
    assert response.status_code == 200


@pytest.mark.parametrize(
    "url, locality", [("/localities/1", "Moscow"), ("/localities/2", "New York")]
)
def test_get_address(client, url, locality):
    test_post_address(client)
    test_post_address(client, address="new york", expected="New York")
    response = client.get(url)
    assert response.status_code == 200
    response = response.get_json()
    assert_keys_match(response["locality"], LOCALITY_KEYS)
    assert locality in response["locality"]["name"]


def test_get_address_forecast(client, 
