import pytest


from today_weather import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_post_address(client):
    response = client.post("/localities", json={"address": "москва"})
    breakpoint
    