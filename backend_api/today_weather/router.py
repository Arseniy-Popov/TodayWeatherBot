from werkzeug.exceptions import HTTPException

from today_weather.config import CONFIG
from today_weather.views import LocalityForecastView, LocalityView


def add_routes(app):
    """
    Register url rules and error handlers with the app.
    """
    _route_view(
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
        """
        Log the exception and return a response with the custom description and code.
        """
        app.logger.exception(exception)
        if isinstance(exception, HTTPException):
            return {"error": exception.description}, exception.code
        return {"error": CONFIG["ERROR"]["GENERAL"]}, 500


def _route_view(
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
