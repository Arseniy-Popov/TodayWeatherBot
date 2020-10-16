#### About

* backend API powering a Telegram bot with a weather forecast for the day
* returns a weather forecast for the remainder of the current day in response to a free form address input
* the backend API, at [api.today-weather.arseniypopov.com](http://api.today-weather.arseniypopov.com), is documented in [redoc](http://api.today-weather.arseniypopov.com/docs/redoc.html) and [swagger](http://api.today-weather.arseniypopov.com/docs/swagger.html) (interactive) formats
* following a POST request to /localities with a free form address input, the server checks if the input maps to any of the saved localities. If not, it sends a request to geocode the input to Google Geocoding API and maps the input to the received locality. The coordinates of the locality, cached or obtained from Google Geocoding API, are sent to OpenWeatherMap API to obtain a weather forecast. It is then processed and returned to the user, together with a reference, /localities/{id}, to the locality
* the telegram bot, at [TodayWeatherBot](https://t.me/AMP_TodayWeatherBot), feeds off the backend API, and supports free form address input, setting a default locality, and requesting forecasts for latest and default localities

#### Built with

* built with `Flask` as a web framework and `marshmallow` for object serialization 
* utilizes `Google Geocoding API` to interpret free-form address input and `OpenWeatherMap API` to obtain weather forecasts
* uses `PostgreSQL` for storing localities and caching the mapping from free-form address inputs to localities with `SQLAlchemy` as an ORM
* tested with `pytest`
* deployed to `AWS EC2` with `nginx` and `gunicorn`; containerized with `Docker` and `docker-compose`
* the telegram bot is deployed to `Heroku`; built with `python-telegram-bot` as a wrapper around Telegram's API; uses `PostgreSQL` and `SQLAlchemy` for storing user's latest and default addresses; tested with `unittest`

#### Sequence diagram for the backend API service

![chart](/backend_api/docs/static/chart.png)
