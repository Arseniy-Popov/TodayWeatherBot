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
# RUN npx redoc-cli bundle -o today_weather/docs/redoc.html spec.yaml
# RUN python swagger-yaml-to-html.py < ./spec.yaml > ./today_weather/docs/swagger.html
CMD gunicorn today_weather.router:app --bind 0.0.0.0:8080