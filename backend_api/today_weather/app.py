from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from flask import Flask
from flask_marshmallow import Marshmallow
from today_weather import db
from today_weather.config import get_db_uri
from today_weather.models import Base


ma = Marshmallow()


def make_app(testing=False):
    """
    Creates instance of app.
    """
    app = Flask(__name__)
    app.config["TESTING"] = testing
    return app


def init_app(app):
    """
    Builds up instance of app.
    """
    db.session, db.engine = init_db(app)
    # to prevent circular imports
    from today_weather.router import add_routes

    ma.init_app(app)
    add_routes(app)
    return app


def init_db(app):
    """
    Creates a session and creates all tables if the db does not already have those.
    """
    engine = create_engine(get_db_uri(app))
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
    return session, engine


if __name__ == "__main__":
    app = make_app()
    app = init_app(app)
    app.run(debug=True)
