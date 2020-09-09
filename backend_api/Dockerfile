FROM python:3.7
WORKDIR /app
COPY Pipfile* ./
RUN pip install pipenv
RUN pipenv install --system --deploy
COPY . ./
CMD gunicorn today_weather.router:app --bind 0.0.0.0:8080