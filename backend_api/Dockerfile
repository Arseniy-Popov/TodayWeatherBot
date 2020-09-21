FROM python:3.7
ENV DOCKER=True
RUN apt-get update
RUN apt-get -y install npm
RUN npm install redoc
WORKDIR /app
COPY Pipfile* ./
RUN pip install pipenv
RUN pipenv install --system --deploy
COPY . ./
CMD gunicorn "today_weather.app:create_app()" --bind 0.0.0.0:8000
