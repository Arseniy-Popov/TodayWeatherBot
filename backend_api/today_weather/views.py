from typing import Dict, Tuple

from flask import abort, request, url_for
from flask.views import MethodView
from flask_api import status

from today_weather.config import CONFIG
from today_weather.db import (
    create_object,
    get_all,
    get_obj_attr,
    get_or_none,
    set_obj_attr,
    write,
)
from today_weather.exceptions import (
    BaseAPIException,
    GeneralError,
    GeocodingError,
    LocalityError,
    NotFoundError,
    WeatherParseError,
)
from today_weather.models import AddressInput, Locality
from today_weather.schemas import locality_schema, weather_schema
from today_weather.utils.geocoding import geocode
from today_weather.utils.misc import log_reply
from today_weather.utils.owmparser import OWMParser


def get_locality(input: str) -> Tuple[Locality, bool]:
    cached_input = get_or_none(model=AddressInput, field="input", value=input)
    if cached_input is None or cached_input.is_expired():
        address, lat, lng = geocode(input)
        locality = get_or_none(Locality, "name", address)
        if not locality:
            locality = create_object(model=Locality, name=address, lat=lat, lng=lng)
            existed = False
        else:
            existed = True
        write(AddressInput(input=input, locality=locality))
    else:
        locality = cached_input.locality
        existed = True
    return locality, existed


def get_weather(locality: Locality) -> Dict:
    try:
        today_weather = OWMParser()(locality.lat, locality.lng)
        return today_weather
    except Exception:
        raise WeatherParseError()


class LocalityView(MethodView):
    def get(self, id):
        print(url_for("localities", id=1))
        locality = get_or_none(Locality, "id", id)
        if not locality:
            abort(status.HTTP_404_NOT_FOUND)
        return ({"locality": locality_schema.dump(locality)}, status.HTTP_200_OK)

    def post(self):
        locality, existed = get_locality(request.json["address"])
        weather = get_weather(locality)
        return (
            {
                "forecast": weather_schema.dump(weather),
                "locality": locality_schema.dump(locality),
            },
            status.HTTP_201_CREATED if not existed else status.HTTP_200_OK,
        )


class LocalityForecastView(MethodView):
    def get(self, id):
        locality = get_or_none(Locality, "id", id)
        if not locality:
            abort(status.HTTP_404_NOT_FOUND)
        weather = get_weather(locality)
        return (
            {
                "forecast": weather_schema.dump(weather),
                "locality": locality_schema.dump(locality),
            },
            status.HTTP_200_OK,
        )
