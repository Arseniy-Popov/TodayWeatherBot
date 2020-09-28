import logging
from typing import Dict, Tuple

import requests

from today_weather.config import CONFIG, GOOG_MAPS_API_KEY
from today_weather.exceptions import GeocodingError, LocalityError


def _make_request(address: str) -> Dict:
    """
    Makes a request to Geocoding API.
    """
    logging.info(f"request to Geocoding API: {address}")
    params = {"address": address, "key": GOOG_MAPS_API_KEY, "language": "en"}
    return requests.get(CONFIG["URL"]["GOOGLE_GEOCODING_URL"], params=params).json()


def _parse_response(response: Dict) -> Tuple[str, float, float]:
    response_results = response["results"][0]
    _check_response(response_results)
    address = response_results["formatted_address"]
    lat = response_results["geometry"]["location"]["lat"]
    lng = response_results["geometry"]["location"]["lng"]
    return address, lat, lng


def _check_response(result):
    """
    Check if the resulting address refers to a city and
    is not too narrow (like street address) or too wide (like a country).
    """
    types = result["types"]
    if "locality" not in types:
        raise LocalityError()


def geocode(address: str) -> Tuple[str, float, float]:
    """
    Geocodes free form address input.
    """
    try:
        return _parse_response(_make_request(address))
    except Exception:
        raise GeocodingError()
