import os

import requests

from dotenv import load_dotenv

load_dotenv()
GOOG_MAPS_API_KEY = os.environ["GOOG_MAPS_API_KEY"]


def make_request(address):
    URL = "https://maps.googleapis.com/maps/api/geocode/json"
    querystring = f"?address={address}&key={GOOG_MAPS_API_KEY}&language=ru"
    return requests.get(URL + querystring).json()


def parse_response(response):
    result = response["results"][0]
    address = result["formatted_address"]
    lat = result["geometry"]["location"]["lat"]
    lng = result["geometry"]["location"]["lng"]
    return address, lat, lng


def geocode(address):
    response = make_request(address)
    return parse_response(response)
