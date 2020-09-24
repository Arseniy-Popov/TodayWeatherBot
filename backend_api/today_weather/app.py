from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from flask import Flask
from flask_marshmallow import Marshmallow
from today_weather import db
from today_weather.config import get_db_uri
from today_weather.models import Base

ma = Marshmallow()


def init_db(app):
    engine = create_engine(get_db_uri(app))
    Session = sessionmaker(bind=engine)
    session = Session()
    # Base.metadata.create_all(engine)
    return session, engine


def drop_db(engine):
    Base.metadata.drop_all(engine)


def make_app(testing=False):
    app = Flask(__name__)
    app.config["TESTING"] = testing
    return app


def init_app(app):
    db.session, db.engine = init_db(app)
    Base.metadata.create_all(db.engine)
    from today_weather.router import init_app

    ma.init_app(app)
    init_app(app)
    return app


def create_app():
    app = make_app()
    app = init_app(app)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
