FROM python:3.7
RUN apt-get update
RUN apt-get -y install npm
RUN npm install redoc
WORKDIR /app/docs
COPY . ./
RUN pip install pipenv
RUN pipenv install --system --deploy
CMD sleep infinity