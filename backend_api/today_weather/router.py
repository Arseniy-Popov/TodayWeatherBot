from werkzeug.exceptions import HTTPException

from today_weather import app, ma
from today_weather.views import LocalityView, LocalityForecastView
from today_weather.exceptions import BaseAPIException
from today_weather.config import CONFIG


@app.errorhandler(Exception)
def error_handler(exception):
    app.logger.exception(exception)
    if isinstance(exception, BaseAPIException):
        return {"error": exception.error_message}, exception.status_code
    elif isinstance(exception, HTTPException):
        return {"error": exception.description}, exception.code
    else:
        return {"error": CONFIG["ERROR"]["GENERAL"]}, 500


def register_api(
    view, endpoint, url, list_methods, detail_methods, pk="id", pk_type="int"
):
    """
    Adds routing for list view at {url} and detail view at {url}/<{pk_type}:{pk}>.
    """
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, view_func=view_func, methods=list_methods)
    app.add_url_rule(
        f"{url}/<{pk_type}:{pk}>", view_func=view_func, methods=detail_methods
    )


register_api(
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


if __name__ == "__main__":
    app.run(debug=True)
