from urllib.parse import unquote
from typing import Tuple, Dict

from flask import Flask, url_for, request, abort
from flask.views import MethodView
from flask_marshmallow import Marshmallow
from werkzeug.exceptions import HTTPException, NotFound
from marshmallow import Schema, INCLUDE

from today_weather.config import CONFIG
from today_weather.db import (
    create_object,
    get_all,
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
ma = Marshmallow(app)


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


class WeatherSchema(Schema):
    class Meta:
        fields = ("temp_min", "temp_max", "rain", "snow")


class LocalitySchema(Schema):
    class Meta:
        fields = ("name", "links", "lat", "lng")

    links = ma.Hyperlinks({"self": ma.URLFor("localities", id="<id>")})


weather_schema = WeatherSchema()
locality_schema = LocalitySchema()


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
            raise NotFoundError()
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


@app.errorhandler(Exception)
def error_handler(exception):
    app.logger.exception(exception)
    if isinstance(exception, BaseAPIException):
        return {"error": exception.error_message}, exception.status_code
    elif isinstance(exception, HTTPException):
        return {"error": exception.description}, exception.code
    else:
        return {"error": CONFIG["ERROR"]["GENERAL"]}, 500


locality_view = LocalityView.as_view("localities")
app.add_url_rule("/localities/<int:id>", view_func=locality_view)
app.add_url_rule("/localities", view_func=locality_view)
app.add_url_rule(
    "/localities/<int:id>/forecast",
    view_func=LocalityForecastView.as_view("locality_forecast"),
)


if __name__ == "__main__":
    app.run(debug=True)
