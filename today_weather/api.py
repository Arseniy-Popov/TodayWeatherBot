from urllib.parse import unquote

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
from today_weather.utils.geocoding import AddressError, geocode
from today_weather.utils.misc import log_reply
from today_weather.utils.owmparser import OWMParser
from today_weather.utils.recommend import Recommender


app = Flask(__name__)
api = Api(app)


def _get_locality(input):
    cached_input = get_or_none(model=AddressInput, field="input", value=input)
    if cached_input is None or cached_input.is_expired():
        try:
            address, lat, lng = geocode(input)
        except AddressError as e:
            raise e
        except Exception as e:
            raise e
        locality = get_or_none(Locality, "name", address)
        if not locality:
            locality = create_object(model=Locality, name=address, lat=lat, lng=lng)
        write(AddressInput(input=input, locality=locality))
    else:
        locality = cached_input.locality
    return locality


def _get_weather(locality):
    try:
        today_weather = OWMParser().get_today_weather(locality.lat, locality.lng)
        return today_weather
    except Exception as e:
        raise e    

        
class Forecast(Resource):
    def get(self, address):
        # try:
        breakpoint()
        locality =  _get_locality(unquote(address))
        weather = _get_weather(locality)
        # except Exception as e:
        #     if isinstance(e, AddressError):
        #         return CONFIG["ERROR"]["GEOCODING_NOT_LOCALITY"], 400
        #     else:
        #         return CONFIG["ERROR"]["GEOCODING_GENERAL"], 400
        response = Recommender(weather).recommend() + "-" * 30 + f"\n{locality.name}"
        self.latest_locality = locality
        return response, 200
        

api.add_resource(Forecast, "/forecast/<address>")


if __name__ == "__main__":
    app.run(debug=True)
