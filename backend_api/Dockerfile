FROM python:3.7
ENV DOCKER=True
WORKDIR /app
COPY Pipfile* ./
RUN pip install pipenv
RUN pipenv install --system --deploy
COPY . ./
CMD gunicorn "today_weather.app:run_app()" --bind 0.0.0.0:8000 
