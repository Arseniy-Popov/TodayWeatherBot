from today_weather.config import CONFIG


class BaseAPIException(Exception):
    status_code = 500
    pass


class LocalityError(BaseAPIException):
    error_message = CONFIG["ERROR"]["GEOCODING_NOT_LOCALITY"]
    status_code = 400
    pass


class GeocodingError(BaseAPIException):
    error_message = CONFIG["ERROR"]["GENERAL"]
    pass


class WeatherParseError(BaseAPIException):
    error_message = CONFIG["ERROR"]["OWM_GENERAL"]
    pass


class GeneralError(BaseAPIException):
    error_message = CONFIG["ERROR"]["GENERAL"]
    pass


class NotFoundError(BaseAPIException):
    error_message = CONFIG["ERROR"]["NOT_FOUND"]
    status_code = 404
    pass
