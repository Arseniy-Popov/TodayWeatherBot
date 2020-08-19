import datetime as dt
import os
import logging
from collections import namedtuple

import requests

from today_weather.config import OWM_API_KEY


class OWMParser:
    def __init__(self):
        self.WeatherData = namedtuple(
            "WeatherData",
            ("dt_start", "dt_end", "temp_min", "temp_max", "rain", "snow"),
        )

    def make_request(self, lat, lng):
        URL = "https://api.openweathermap.org/data/2.5/forecast"
        params = {"lat": lat, "lon": lng, "appid": OWM_API_KEY, "units": "metric"}
        logging.info(f"request to OWM API")
        return requests.get(URL, params=params).json()

    def parse_weather_data(self, response):
        self.timezone = dt.timezone(dt.timedelta(seconds=response["city"]["timezone"]))
        return [
            self.populate_weather_data(weather_item)
            for weather_item in response["list"]
        ]

    def populate_weather_data(self, weather_item):
        dt_start = dt.datetime.fromtimestamp(weather_item["dt"], tz=self.timezone)
        dt_end = dt_start + dt.timedelta(hours=3)
        temp_min, temp_max = (
            weather_item["main"]["temp_min"],
            weather_item["main"]["temp_max"],
        )
        try:
            rain = weather_item["rain"]["3h"]
        except KeyError:
            rain = False
        try:
            snow = weather_item["snow"]["3h"]
        except KeyError:
            snow = False
        return self.WeatherData(dt_start, dt_end, temp_min, temp_max, rain, snow)

    def filter_today_weather_data(self, weather_data):
        today = dt.datetime.now(tz=self.timezone)
        cutoff = today.replace(day=today.day + 1, hour=3)
        return [item for item in weather_data if item.dt_start < cutoff]

    def aggregate_weather(self, weather_data):
        temp_min = min(i.temp_min for i in weather_data)
        temp_max = max(i.temp_max for i in weather_data)
        rain = any(i.rain for i in weather_data)
        snow = any(i.snow for i in weather_data)
        return temp_min, temp_max, rain, snow

    def get_today_weather(self, lat, lng):
        response = self.make_request(lat, lng)
        weather_data = self.parse_weather_data(response)
        weather_data = self.filter_today_weather_data(weather_data)
        return self.aggregate_weather(weather_data)
