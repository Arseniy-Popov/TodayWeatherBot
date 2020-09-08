from today_weather import ma


class WeatherSchema(ma.Schema):
    class Meta:
        fields = ("temp_min", "temp_max", "rain", "snow")


class LocalitySchema(ma.Schema):
    class Meta:
        fields = ("name", "links", "lat", "lng")

    links = ma.Hyperlinks({"self": ma.URLFor("localities", id="<id>")})


weather_schema = WeatherSchema()
locality_schema = LocalitySchema()
