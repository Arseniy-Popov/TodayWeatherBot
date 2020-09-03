from today_weather.config import CONFIG


class LocalityError(Exception):
    """
    Address not a locality.
    """

    error_message = CONFIG["ERROR"]["GEOCODING_NOT_LOCALITY"]

    pass


class GeocodingError(Exception):
    error_message = CONFIG["ERROR"]["GENERAL"]
    pass


class WeatherParseError(Exception):
    error_message = CONFIG["ERROR"]["OWM_GENERAL"]
    pass


class GeneralError(Exception):
    error_message = CONFIG["ERROR"]["GENERAL"]
    pass
