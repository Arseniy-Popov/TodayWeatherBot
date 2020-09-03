from urllib.parse import unquote
from typing import Tuple

from flask import Flask, url_for, request
from flask.views import MethodView

from today_weather.config import CONFIG
from today_weather.db import (
    create_object,
    get_obj_attr,
    get_or_none,
    set_obj_attr,
    write,
)
from today_weather.models import AddressInput, Locality, User
from today_weather.exceptions import (
    WeatherParseError,
    GeocodingError,
    LocalityError,
    GeneralError,
)
from today_weather.utils.geocoding import geocode
from today_weather.utils.misc import log_reply
from today_weather.utils.owmparser import OWMParser
from today_weather.utils.recommend import Recommender


app = Flask(__name__)


def get_locality(input: str) -> Locality:
    cached_input = get_or_none(model=AddressInput, field="input", value=input)
    if cached_input is None or cached_input.is_expired():
        try:
            address, lat, lng = geocode(input)
        except LocalityError as e:
            raise e
        except Exception:
            raise GeocodingError()
        locality = get_or_none(Locality, "name", address)
        if not locality:
            locality = create_object(model=Locality, name=address, lat=lat, lng=lng)
        write(AddressInput(input=input, locality=locality))
    else:
        locality = cached_input.locality
    return locality


def get_weather(locality: Locality) -> Tuple[int, int, bool, bool]:
    try:
        today_weather = OWMParser().get_today_weather(locality.lat, locality.lng)
        return today_weather
    except Exception:
        raise WeatherParseError()


def error_message(exception):
    if hasattr(exception, "error_message"):
        message = exception.error_message
    else:
        message = GeneralError().error_message
    return {"error": message}, 400


def generate_user_response(
    weather: Tuple[int, int, bool, bool], locality: Locality
) -> str:
    return Recommender(weather).recommend() + "-" * 30 + f"\n{locality.name}"


class ForecastView(MethodView):
    def post(self) -> Tuple[dict, int]:
        try:
            locality = get_locality(request.json["address"])
            weather = get_weather(locality)
        except Exception as e:
            return error_message(e)
        response = generate_user_response(weather, locality)
        return (
            {"response": response, "locality": url_for("locality", id=locality.id)},
            200,
        )


class LocalityView(MethodView):
    def get(self, id: int) -> Tuple[int, int]:
        locality = get_or_none(Locality, "id", id)
        return {"locality": locality.name}


class LocalityForecast(MethodView):
    def get(self, id):
        locality = get_or_none(Locality, "id", id)
        if not locality:
            return {"error": "no such locality"}, 400
        try:
            weather = get_weather(locality)
        except Exception as e:
            return error_message(e)
        response = generate_user_response(weather, locality)
        return (
            {"response": response, "locality": url_for("locality", id=locality.id)},
            200,
        )


app.add_url_rule("/forecast", view_func=ForecastView.as_view("forecast_by_string"))
app.add_url_rule("/locality/<int:id>", view_func=LocalityView.as_view("locality"))
app.add_url_rule(
    "/locality/<int:id>/forecast",
    view_func=LocalityForecast.as_view("locality_forecast"),
)


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port="8080", debug=True)
    app.run(debug=True)
