__`Python` `Flask` `PostgreSQL` `SQLAlchemy` `pytest` `unittest` `Google Geocoding API` `OpenWeatherMap API` `Docker` `docker-compose` `AWS EC2` `Heroku` `marshmallow` `python-telegram-bot` `pyrogram` `gunicorn` `nginx`__

#### About

* Backend API powering a Telegram bot with a weather forecast for the day. Returns a weather forecast for the remainder of the current day in response to a free form address input.
* The telegram bot, at [TodayWeatherBot](https://t.me/AMP_TodayWeatherBot), feeds off the backend API, and supports free form address input, setting a default locality, and requesting forecasts for latest and default localities.

#### Built with

* Built with `Flask` as a web framework and `marshmallow` for object serialization; utilizes `Google Geocoding API` to interpret free-form address input and `OpenWeatherMap API` to obtain weather forecasts; uses `PostgreSQL` for storing localities and caching the mapping from free-form address inputs to localities with `SQLAlchemy` as an ORM; tested with `pytest`;deployed to `AWS EC2` with `nginx` and `gunicorn`; containerized with `Docker` and `docker-compose`.
* The telegram bot is deployed to `Heroku`; built with `python-telegram-bot` as a wrapper around Telegram's API; uses `PostgreSQL` and `SQLAlchemy` for storing user's latest and default addresses; tested with `unittest`.

