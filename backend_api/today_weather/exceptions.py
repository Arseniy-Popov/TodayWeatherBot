from werkzeug.exceptions import HTTPException

from today_weather.config import CONFIG


class BaseCustomException(HTTPException):
    code = 500


class LocalityError(BaseCustomException):
    description = CONFIG["ERROR"]["GEOCODING_NOT_LOCALITY"]
    code = 400


class GeocodingError(BaseCustomException):
    description = CONFIG["ERROR"]["GENERAL"]


class WeatherParseError(BaseCustomException):
    description = CONFIG["ERROR"]["OWM_GENERAL"]


class GeneralError(BaseCustomException):
    description = CONFIG["ERROR"]["GENERAL"]


class NotFoundError(BaseCustomException):
    description = CONFIG["ERROR"]["NOT_FOUND"]
    code = 404
