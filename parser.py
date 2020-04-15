import datetime as dt
import os
from collections import namedtuple

import requests
from dotenv import load_dotenv

load_dotenv()
OWM_API_KEY = os.environ["OWM_API_KEY"]


WeatherData = namedtuple(
    "WeatherData", ("dt_start", "dt_end", "temp_min", "temp_max", "rain", "snow")
)


def make_request(lat, lng):
    URL = "https://api.openweathermap.org/data/2.5/forecast"
    querystring = f"?lat={lat}&lon={lng}&appid={OWM_API_KEY}&units=metric"
    return requests.get(URL + querystring).json()


def parse_weather_data(response):
    timezone, result = response["city"]["timezone"], []
    for weather_item in response["list"]:
        result.append(populate_weather_data(weather_item, timezone))
    return result


def populate_weather_data(weather_item, timezone):
    timezone = dt.timezone(dt.timedelta(seconds=timezone))
    dt_start = dt.datetime.fromtimestamp(weather_item["dt"], tz=timezone)
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
    return WeatherData(dt_start, dt_end, temp_min, temp_max, rain, snow)


def filter_today_weather_data(weather_data):
    result, today = [], dt.datetime.now(tz=weather_data[0].dt_start.tzinfo)
    for item in weather_data:
        if item.dt_start <= today.replace(day=today.day + 1, hour=3):
            result.append(item)
    return result


def aggregate_weather(weather_data):
    temp_min = min(i.temp_min for i in weather_data)
    temp_max = max(i.temp_max for i in weather_data)
    rain = any(i.rain for i in weather_data)
    snow = any(i.snow for i in weather_data)
    return temp_min, temp_max, rain, snow


def get_today_weather(lat, lng):
    response = make_request(lat, lng)
    weather_data = parse_weather_data(response)
    weather_data = filter_today_weather_data(weather_data)
    return aggregate_weather(weather_data)
