import logging
import os

import dotenv
import requests

from today_weather.config import GOOG_MAPS_API_KEY
from today_weather.exceptions import GeocodingError


def make_request(address):
    URL = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOG_MAPS_API_KEY, "language": "en"}
    logging.info(f"request to Geocoding API: {address}")
    return requests.get(URL, params=params).json()


def parse_response(response):
    response_results = response["results"][0]
    check_response(response_results)
    address = response_results["formatted_address"]
    lat = response_results["geometry"]["location"]["lat"]
    lng = response_results["geometry"]["location"]["lng"]
    return address, lat, lng


def check_response(result):
    types = result["types"]
    if "locality" not in types:
        raise LocalityError()


def geocode(address):
    response = make_request(address)
    try:
        return parse_response(response)
    except Exception:
        raise GeocodingError()
