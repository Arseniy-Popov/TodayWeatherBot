import os

import requests
import dotenv

import config


def make_request(address):
    URL = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": config.GOOG_MAPS_API_KEY, "language": "en"}
    return requests.get(URL, params=params).json()


def parse_response(response):
    result = response["results"][0]
    address = result["formatted_address"]
    lat = result["geometry"]["location"]["lat"]
    lng = result["geometry"]["location"]["lng"]
    return address, lat, lng


def geocode(address):
    response = make_request(address)
    return parse_response(response)
