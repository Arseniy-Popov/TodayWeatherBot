class Recommender:
    def __init__(self, aggregate_weather):
        self.temp_min, self.temp_max, self.rain, self.snow = aggregate_weather
        self.temp_min, self.temp_max = round(self.temp_min), round(self.temp_max)
        self.result = []

    def _temparature_range(self):
        if self.temp_min == self.temp_max:
            result = f"Температура: {self.temp_max}\u00B0C \n"
        else:
            result = (
                f"Температура: от {self.temp_min}\u00B0C до {self.temp_max}\u00B0C \n"
            )
        self.result.append(result)

    def _rain_snow(self):
        if self.rain:
            self.result.append(f"+ дождь \n")
        if self.snow:
            self.result.append(f"+ снег \n")

    def _apparel(self):
        if self.rain:
            self.result.append(f"Возьми зонт! \n")

    def recommend(self):
        self._temparature_range()
        self._rain_snow()
        self._apparel()
        return "".join(self.result)
