import datetime
import json
import pandas
from collections import namedtuple
import sys
from pathlib import Path
sys.path.append('../')
from TFTask.TFTask import TFTask
from TFBikesGetter.TFBikesCreator import TFBikesCreator
from TFCarsGetter.TFCarsCreatorDaily import TFCarsCreatorDaily
from TFWeatherGetter.TFWUWeatherCreator import TFWUWeatherCreator
from TFArchiveGetter.TFArchiveCreator import TFArchiveCreator
from TFModel.TFModel import TFModel
from TFWeatherGetter.TFWeatherForecastGetter import TFWeatherForecastGetter
from TFTypes.TFTypes import ForecastArchiveRow


class TFUpdateTask:

    def __init__(self, path):
        self.__path = path
        self.__bc = TFBikesCreator(self.__path + 'Bikes.csv')
        self.__cc = TFCarsCreatorDaily(self.__path + 'ten_minutes.csv')
        self.__wc = TFWUWeatherCreator(self.__path + 'Weather.csv')
        self.__ac = TFArchiveCreator(self.__path + 'Archive.csv')
        self.__mc = TFModel()

    def task(self):
        now = datetime.datetime.now()
        tday = now + datetime.timedelta(days=1)
        yday = now - datetime.timedelta(days=1)
        bikes = self.__bc.download_last_day(yday)
        cars = self.__cc.create_daily(yday, self.__path + 'Cars.csv')
        [temp, precip] = self.__wc.download_weather(yday)
        self.__ac.add_new_row(yday, [cars, bikes, temp, precip])
        self.__mc.create_model(self.__path + 'Archive.csv')

        [t_temp, t_precip, da_t_temp, da_t_precip] = TFWeatherForecastGetter.Get_Forecast(now)

        t_bikes_fc = self.__mc.get_bikes(now, t_temp, t_precip)
        t_cars_fc = self.__mc.get_cars(now, t_temp, t_precip)

        da_t_bikes_fc = self.__mc.get_bikes(now, da_t_temp, da_t_precip)
        da_t_cars_fc = self.__mc.get_cars(now, da_t_temp, da_t_precip)

        json_data = json.dumps({'cars_tomorrow': t_cars_fc, 'cars_day_after_tomorrow': da_t_cars_fc,
                               'bikes_tomorrow': t_bikes_fc, 'bikes_day_after_tomorrow': da_t_bikes_fc})

        with open(self.__path + 'forecaster.json', 'w', encoding='utf-8') as outfile:
            json.dump(json_data, outfile)

        self.__save_forecast([t_cars_fc, t_bikes_fc], tday)

    def __save_forecast(self, row, day):

        if Path(self.__path + 'ForecastArchive.csv').is_file():
            out_df = pandas.read_csv(self.__path + 'ForecastArchive.csv', index_col='date')
        else:
            out_df = pandas.DataFrame(columns=ForecastArchiveRow._fields)
            out_df.set_index('date')
            del out_df['date']

        out_df.loc[day.strftime('%Y-%m-%d')] = row
        new_index = [day.strftime('%Y-%m-%d')] + [ind for ind in out_df.index if ind != day.strftime('%Y-%m-%d')]
        out_df = out_df.reindex(index=new_index)
        out_df['date'] = out_df.index

        out_df.to_csv(self.__path + 'ForecastArchive.csv', index=False)