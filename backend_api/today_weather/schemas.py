from today_weather.app import ma


class WeatherSchema(ma.Schema):
    class Meta:
        fields = ("temp_min", "temp_max", "rain", "snow")


class LocalitySchema(ma.Schema):
    class Meta:
        fields = ("name", "links", "lat", "lng")

    links = ma.Hyperlinks({"self": ma.URLFor("localities", id="<id>", _method="GET")})


weather_schema = WeatherSchema()
locality_schema = LocalitySchema()
