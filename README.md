* a combibation of a backend API and a user-facing telegram bot

* the API, at [api.today-weather.arseniypopov.com](http://api.today-weather.arseniypopov.com), is documented in [redoc](http://api.today-weather.arseniypopov.com/docs/redoc.html) and [swagger](http://api.today-weather.arseniypopov.com/docs/swagger.html) formats
* built with `Flask` as a web framework and `marshmallow` for object serialization 
* utilizes `Google Geocoding API` to interpret free-form address input and `OpenWeatherMap API` to obtain weather forecasts
* uses `PostgreSQL` for caching the mapping from free-form address inputs to geographic localities with `SQLAlchemy` as an ORM
* deployed to `AWS EC2` with `nginx` and `gunicorn`; containerized with `Docker` and `docker-compose`  


![chart](http://api.today-weather.arseniypopov.com/docs/chart.png)

* deployed to `Heroku` at https://t.me/AMP_TodayWeatherBot
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
