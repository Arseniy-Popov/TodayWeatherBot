class Recommender:
    def __init__(self, weather):
        self.temp_min, self.temp_max, self.rain, self.snow = (
            weather["temp_min"],
            weather["temp_max"],
            weather["rain"],
            weather["snow"],
        )
        self.temp_min, self.temp_max = round(self.temp_min), round(self.temp_max)
        self.result = []

    def _temparature_range(self):
        if self.temp_min == self.temp_max:
            result = f"{self.temp_max}\u00B0C \n"
        else:
            result = f"{self.temp_min}\u00B0C to {self.temp_max}\u00B0C \n"
        self.result.append(result)

    def _rain_snow(self):
        if self.rain:
            self.result.append(f"+ rain \n")
        if self.snow:
            self.result.append(f"+ snow \n")

    def _apparel(self):
        if self.rain:
            self.result.append(f"Take your umbrella. \n")

    def __call__(self):
        self._temparature_range()
        self._rain_snow()
        self._apparel()
        return "".join(self.result)
