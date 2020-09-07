from urllib.parse import unquote
from typing import Tuple

from flask import Flask, url_for, request, abort
from flask.views import MethodView
from werkzeug.exceptions import HTTPException, NotFound
from marshmallow import Schema, INCLUDE

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
    BaseAPIException,
    WeatherParseError,
    GeocodingError,
    LocalityError,
    GeneralError,
    NotFoundError,
)
from today_weather.utils.geocoding import geocode
from today_weather.utils.misc import log_reply
from today_weather.utils.owmparser import OWMParser
from today_weather.utils.recommend import Recommender


app = Flask(__name__)


def get_locality(input):
    cached_input = get_or_none(model=AddressInput, field="input", value=input)
    if cached_input is None or cached_input.is_expired():
        address, lat, lng = geocode(input)
        locality = get_or_none(Locality, "name", address)
        if not locality:
            locality = create_object(model=Locality, name=address, lat=lat, lng=lng)
        write(AddressInput(input=input, locality=locality))
    else:
        locality = cached_input.locality
    return locality


def get_weather(locality):
    try:
        today_weather = OWMParser()(locality.lat, locality.lng)
        return today_weather
    except Exception:
        raise WeatherParseError()


class WeatherSchema(Schema):
    class Meta:
        fields = ("temp_min", "temp_max", "created_at", "uppername")


class ForecastView(MethodView):
    def post(self):
        locality = get_locality(request.json["address"])
        weather = get_weather(locality)
        weather_schema = WeatherSchema()
        return (
            {
                "forecast": weather,
                "locality": url_for("locality", id=locality.id),
            },
            200,
        )


class LocalityView(MethodView):
    def get(self, id):
        locality = get_or_none(Locality, "id", id)
        if not locality:
            raise NotFoundError()
        return {"locality": locality.name}


class LocalityForecastView(MethodView):
    def get(self, id):
        locality = get_or_none(Locality, "id", id)
        if not locality:
            raise NotFoundError()
        weather = get_weather(locality)
        response = generate_user_response(weather, locality)
        return (
            {"response": response, "locality": url_for("locality", id=locality.id)},
            200,
        )


@app.errorhandler(Exception)
def error_handler(exception):
    app.logger.exception(exception)
    if isinstance(exception, BaseAPIException):
        return {"error": exception.error_message}, exception.status_code
    elif isinstance(exception, HTTPException):
        return {"error": exception.description}, exception.code
    else:
        return {"error": CONFIG["ERROR"]["GENERAL"]}, 500


app.add_url_rule("/forecast", view_func=ForecastView.as_view("forecast_by_string"))
app.add_url_rule("/locality/<int:id>", view_func=LocalityView.as_view("locality"))
app.add_url_rule(
    "/locality/<int:id>/forecast",
    view_func=LocalityForecastView.as_view("locality_forecast"),
)


if __name__ == "__main__":
    app.run(debug=True)
