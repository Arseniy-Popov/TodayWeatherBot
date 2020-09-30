from __future__ import annotations

import datetime as dt
import logging
from collections import namedtuple
from typing import Dict, Iterable, List

import requests

from today_weather.config import CONFIG, OWM_API_KEY


WeatherForecast = namedtuple(
    "WeatherForecast", ("temp_min", "temp_max", "rain", "snow")
)


class OWMParser:
    WeatherDatum = namedtuple(
        "WeatherData", ("dt_start", "dt_end", "temp_min", "temp_max", "rain", "snow")
    )

    def __call__(self, lat: float, lng: float) -> WeatherForecast:
        """
        Returns weather forecast for the coordinates.
        """
        data = self._make_request(lat, lng)
        data = self._parse_weather_data(data)
        data = self._filter_today(data)
        return self._aggregate_weather(data)

    def _make_request(self, lat: float, lng: float) -> Dict:
        """
        Makes a request to the OpenWeatherMap API.
        """
        logging.info(f"request to OWM API")
        params = {"lat": lat, "lon": lng, "appid": OWM_API_KEY, "units": "metric"}
        return requests.get(CONFIG["URL"]["OWM_URL"], params=params).json()

    def _parse_weather_data(self, response: Dict) -> List[self.WeatherDatum]:
        """
        Collects all the forecast data points from the OWM response.
        """
        self.timezone = dt.timezone(dt.timedelta(seconds=response["city"]["timezone"]))
        return [
            self._populate_weather_datum(weather_item)
            for weather_item in response["list"]
        ]

    def _populate_weather_datum(self, weather_item: Dict) -> self.WeatherDatum:
        """
        Populates a single weather forecast data point.
        """
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
        return self.WeatherDatum(dt_start, dt_end, temp_min, temp_max, rain, snow)

    def _filter_today(
        self, weather_data: Iterable[self.WeatherDatum]
    ) -> List[self.WeatherDatum]:
        """
        Filters weather forecast data points for the current day.
        """
        today = dt.datetime.now(tz=self.timezone)
        try:
            cutoff = today.replace(day=today.day + 1, hour=4)
        except ValueError:
            cutoff = today.replace(day=1, month=today.month + 1, hour=4)
        return [item for item in weather_data if item.dt_start < cutoff]

    def _aggregate_weather(self, weather_data: Iterable[self.WeatherDatum]) -> Dict:
        """
        Aggregates data across the provided weather forecast data points.
        """
        return WeatherForecast(
            temp_min=min(i.temp_min for i in weather_data),
            temp_max=max(i.temp_max for i in weather_data),
            rain=any(i.rain for i in weather_data),
            snow=any(i.snow for i in weather_data),
        )
