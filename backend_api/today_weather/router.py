from flask_marshmallow import Marshmallow
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.exceptions import HTTPException

from today_weather import make_app
from today_weather.config import CONFIG, get_db_uri
from today_weather.exceptions import BaseAPIException
from today_weather.views import LocalityForecastView, LocalityView
from today_weather.models import Base


def register_api(
    app, view, endpoint, url, list_methods, detail_methods, pk="id", pk_type="int"
):
    """
    Adds routing for list view at {url} and detail view at {url}/<{pk_type}:{pk}>.
    """
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, view_func=view_func, methods=list_methods)
    app.add_url_rule(
        f"{url}/<{pk_type}:{pk}>", view_func=view_func, methods=detail_methods
    )


def make_session(app):
    engine = create_engine(get_db_uri(app))
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
    return session


def init_app(app):
    register_api(
        app=app,
        view=LocalityView,
        endpoint="localities",
        url="/localities",
        list_methods=["POST"],
        detail_methods=["GET"],
    )
    app.add_url_rule(
        "/localities/<int:id>/forecast",
        view_func=LocalityForecastView.as_view("locality_forecast"),
    )

    @app.errorhandler(Exception)
    def error_handler(exception):
        app.logger.exception(exception)
        if isinstance(exception, BaseAPIException):
            return {"error": exception.error_message}, exception.status_code
        elif isinstance(exception, HTTPException):
            return {"error": exception.description}, exception.code
        else:
            return {"error": CONFIG["ERROR"]["GENERAL"]}, 500

    app.session = make_session(app)
    app.ma = Marshmallow(app)
    return app


if __name__ == "__main__":
    app = make_app()
    app = init_app(app)
    app.run(debug=True)
