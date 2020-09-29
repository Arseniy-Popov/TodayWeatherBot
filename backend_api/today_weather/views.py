from typing import Tuple

from flask import abort, request
from flask.views import MethodView
from flask_api import status

from today_weather.db import get_or_none, write
from today_weather.exceptions import WeatherParseError
from today_weather.models import AddressInput, Locality
from today_weather.schemas import locality_schema, weather_schema
from today_weather.utils.geocoding import geocode
from today_weather.utils.owmparser import OWMParser, WeatherForecast


def _get_locality(input: str) -> Tuple[Locality, bool]:
    """
    Get locality corresponding to the given free-form address input. Checks if
    the free-form address input is mapped to any of the saved localities.
    If not, requests the address to be geocoded and maps the address input
    to the obtained locality.
    """
    cached_input = get_or_none(model=AddressInput, field="input", value=input)
    if cached_input is None or cached_input.is_expired():
        address, lat, lng = geocode(input)
        locality = get_or_none(Locality, "name", address)
        if not locality:
            locality = write(Locality(name=address, lat=lat, lng=lng))
            existed = False
        else:
            existed = True
        write(AddressInput(input=input, locality=locality))
    else:
        locality = cached_input.locality
        existed = True
    return locality, existed


def _get_weather(locality: Locality) -> WeatherForecast:
    """
    Get weather forecast for the locality.
    """
    try:
        today_weather = OWMParser()(locality.lat, locality.lng)
    except Exception:
        raise WeatherParseError()
    return today_weather


class LocalityView(MethodView):
    def get(self, id):
        """
        GET /localities/<id>
        """
        locality = get_or_none(Locality, "id", id)
        if not locality:
            abort(status.HTTP_404_NOT_FOUND)
        return ({"locality": locality_schema.dump(locality)}, status.HTTP_200_OK)

    def post(self):
        """
        POST /localities
        """
        locality, existed = _get_locality(request.json["address"])
        weather = _get_weather(locality)
        return (
            {
                "forecast": weather_schema.dump(weather),
                "locality": locality_schema.dump(locality),
            },
            status.HTTP_201_CREATED if not existed else status.HTTP_200_OK,
        )


class LocalityForecastView(MethodView):
    def get(self, id):
        """
        GET /localities/<id>/forecast
        """
        locality = get_or_none(Locality, "id", id)
        if not locality:
            abort(status.HTTP_404_NOT_FOUND)
        weather = _get_weather(locality)
        return (
            {
                "forecast": weather_schema.dump(weather),
                "locality": locality_schema.dump(locality),
            },
            status.HTTP_200_OK,
        )
