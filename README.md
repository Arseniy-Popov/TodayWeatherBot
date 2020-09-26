#### About

* a combination of a backend API and a user-facing telegram bot
* returns a weather forecast for the remainder of the current day in response to a free form address input
* the backend API, at [api.today-weather.arseniypopov.com](http://api.today-weather.arseniypopov.com), is documented in [redoc](http://api.today-weather.arseniypopov.com/docs/redoc.html) and [swagger](http://api.today-weather.arseniypopov.com/docs/swagger.html) formats
* following a POST request to /localities with a free form address input, the server checks if "москва" maps to any of the saved localities. If not, it sends a request to geocode "москва" to Google Geocoding API and maps "москва" to the received locality. The coordinates of the locality, cached or obtained from Google Geocoding API, are sent to OpenWeatherMap API to obtain a weather forecast. It is then processed and returned to the user, together with a reference, /localities/{id}, to the locality
* the telegram bot, at https://t.me/AMP_TodayWeatherBot, feeds off the backend API, and supports free form address input, setting a default locality, and requesting forecasts for latest and default localities

#### Built with

* built with `Flask` as a web framework and `marshmallow` for object serialization 
* utilizes `Google Geocoding API` to interpret free-form address input and `OpenWeatherMap API` to obtain weather forecasts
* uses `PostgreSQL` for caching the mapping from free-form address inputs to geographic localities with `SQLAlchemy` as an ORM
* tested with `pytest`
* deployed to `AWS EC2` with `nginx` and `gunicorn`; containerized with `Docker` and `docker-compose`
* the telegram bot is deployed to `Heroku`; built with `python-telegram-bot` as a wrapper around Telegram's API; uses `PostgreSQL` and `SQLAlchemy` for storing user's latest and default addresses; tested with `unittest`

#### Sequence diagram for the backend API service

![chart](http://api.today-weather.arseniypopov.com/docs/chart.png)

* deployed to `Heroku` at 
* built with `python-telegram-bot` as a wrapper around Telegram's API
* applies `unittest` as a testing framework and `pyrogram` as Telegram API wrapper for integration testing allowing
to test both the development version (with database and client resets between tests) and the deployed version

- TodayWeatherBot
   - [Pipfile](Pipfile)
   - [Pipfile.lock](Pipfile.lock)
   - [Procfile](Procfile)
   - [README.md](README.md)
   - [config.ini](config.ini)
   - today\_weather
     - [\_\_init\_\_.py](today_weather/__init__.py)
     - [\_\_main\_\_.py](today_weather/__main__.py)
     - [bot.py](today_weather/bot.py)
     - [config.py](today_weather/config.py)
     - [db.py](today_weather/db.py): __utilities to communicate with the database__
     - [handlers.py](today_weather/handlers.py): __handlers to orchestrate the core logic__
     - [models.py](today_weather/models.py): __database models__
     - tests
       - [\_\_init\_\_.py](today_weather/tests/__init__.py)
       - [tests.py](today_weather/tests/tests.py): __tests__
     - utils
       - [\_\_init\_\_.py](today_weather/utils/__init__.py)
       - [geocoding.py](today_weather/utils/geocoding.py): __interpreting address input w/ the Geocoding API__
       - [misc.py](today_weather/utils/misc.py)
       - [owmparser.py](today_weather/utils/owmparser.py): __getting weather forecast w/ the OpenWeatherMap API__
       - [recommend.py](today_weather/utils/recommend.py): __devising a response for the user__
