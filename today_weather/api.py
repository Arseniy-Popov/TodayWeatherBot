from urllib.parse import unquote
from typing import Tuple

from flask import Flask
from flask_restful import Resource, Api

from today_weather.config import CONFIG
from today_weather.db import (
    create_object,
    get_obj_attr,
    get_or_none,
    set_obj_attr,
    write,
)
from today_weather.models import AddressInput, Locality, User
from today_weather.exceptions import WeatherParseError, GeocodingError, LocalityError, GeneralError
from today_weather.utils.geocoding import geocode
from today_weather.utils.misc import log_reply
from today_weather.utils.owmparser import OWMParser
from today_weather.utils.recommend import Recommender


app = Flask(__name__)
api = Api(app)


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
        return exception.error_message, 400
    else:
        return GeneralError().error_message, 400
        
class Forecast(Resource):
    def get(self, address: str) -> Tuple[str, int]:
        try:
            locality =  get_locality(address)
            weather = get_weather(locality)
        except Exception as e:
            return error_message(e)
        response = Recommender(weather).recommend() + "-" * 30 + f"\n{locality.name}"
        return response, 200
        

class Locality(Resource):
    def get(self, address: str) -> Tuple[int, int]:
        # try:
        locality =  get_locality(address)
        # except Exception as e:
            # return error_message(e), 400
        return locality.id


api.add_resource(Forecast, "/forecast/<address>")
api.add_resource(Locality, "/locality/<address>")


if __name__ == "__main__":
    app.run(debug=True)
