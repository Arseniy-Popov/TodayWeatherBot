from typing import Dict, Tuple

from flask import abort, request, url_for
from flask.views import MethodView

from today_weather.config import CONFIG
from today_weather.schemas import weather_schema, locality_schema
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
from today_weather.models import AddressInput, Locality, User
from today_weather.utils.geocoding import geocode
from today_weather.utils.misc import log_reply
from today_weather.utils.owmparser import OWMParser
from today_weather.utils.recommend import Recommender


def get_locality(input: str) -> Locality:
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


def get_weather(locality: Locality) -> Dict:
    try:
        today_weather = OWMParser()(locality.lat, locality.lng)
        return today_weather
    except Exception:
        raise WeatherParseError()


class ListDetailViewMixin:
    """
    Routes .get requests to either the .list or the .detail method
    depending on whether an identifier has been supplied. 
    """

    def get(self, id=None):
        if id is not None:
            return self.detail(id)
        return self.list()


class LocalityView(MethodView, ListDetailViewMixin):
    def detail(self, id):
        locality = get_or_none(Locality, "id", id)
        if not locality:
            abort(404)
        return ({"locality": locality_schema.dump(locality)}, 200)

    def list(self):
        localities = get_all(Locality)
        return ({"localities": locality_schema.dump(localities, many=True)}, 200)

    def post(self):
        locality = get_locality(request.json["address"])
        weather = get_weather(locality)
        return (
            {
                "forecast": weather_schema.dump(weather),
                "locality": locality_schema.dump(locality),
            },
            201,
        )


class LocalityForecastView(MethodView):
    def get(self, id):
        locality = get_or_none(Locality, "id", id)
        if not locality:
            abort(404)
        weather = get_weather(locality)
        return (
            {
                "forecast": weather_schema.dump(weather),
                "locality": locality_schema.dump(locality),
            },
            200,
        )
