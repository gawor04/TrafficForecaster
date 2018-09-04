import requests
import datetime

class TFWeatherForecastGetter:

    @staticmethod
    def Get_Forecast(day):

        tomorrow= day + datetime.timedelta(days=1)
        da_tomorrow = tomorrow + datetime.timedelta(days=1)

        forecast_json = TFWeatherForecastGetter.__Get_Forecast_JSON()

        tomorrow_precip = 0.0
        tomorrow_temp = 0.0
        da_tomorrow_precip = 0.0
        da_tomorrow_temp = 0.0

        for date in forecast_json:

            if (int(date['date']['year']) == tomorrow.year and int(date['date']['month']) == tomorrow.month
            and int(date['date']['day']) == tomorrow.day):
                tomorrow_temp = (float(date['high']['celsius']) + float(date['low']['celsius']))/2
                tomorrow_precip = float(date['qpf_day']['mm'])

            elif (int(date['date']['year']) == da_tomorrow.year and int(date['date']['month']) == da_tomorrow.month
            and int(date['date']['day']) == da_tomorrow.day):
                da_tomorrow_temp = (float(date['high']['celsius']) + float(date['low']['celsius']))/2
                da_tomorrow_precip = float(date['qpf_day']['mm'])

        return [tomorrow_temp, tomorrow_precip, da_tomorrow_temp, da_tomorrow_precip]

    @staticmethod
    def __Get_Forecast_JSON():

        r = requests.get("http://api.wunderground.com/api/08704a121bcb1363/forecast/lang:PL/q/PL/Krak%C3%B3w.json")

        while r.status_code != 200:
            r = requests.get("http://api.wunderground.com/api/08704a121bcb1363/forecast/lang:PL/q/PL/Krak%C3%B3w.json")

        return r.json()['forecast']['simpleforecast']['forecastday']