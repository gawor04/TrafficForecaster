import pandas
import numpy
import logging
import json
import sys
import datetime
from pathlib import Path
sys.path.append('../')
from TFBikesGetter.TFBikesCreator import TFBikesCreator
from TFCarsGetter.TFCarsCreatorDaily import TFCarsCreatorDaily
from TFWeatherGetter.TFWUWeatherCreator import TFWUWeatherCreator
from TFWeatherGetter.TFWeatherForecastGetter import TFWeatherForecastGetter
from TFTypes.TFTypes import ArchiveRow
from TFArchiveGetter.TFArchiveCreator import TFArchiveCreator
sys.path.append('./TFInitializer')
from TFModel.TFModel import TFModel
from TFTypes.TFTypes import ForecastArchiveRow

class TFInitializer:

    __PATH = './'

    @staticmethod
    def Init(archive_creator, path):
        TFInitializer.__PATH = path
        out_df = pandas.DataFrame(columns=ArchiveRow._fields)
        out_df.set_index('date')
        del out_df['date']

        TFInitializer.__InitBikes(out_df)
        TFInitializer.__InitCars(out_df)
        TFInitializer.__InitWeather(out_df)

        out_df['date'] = out_df.index
        archive_creator.create(out_df)
        TFInitializer.__calculate_forecast()

    @staticmethod
    def __InitBikes(out_df):
        bc = TFBikesCreator(TFInitializer.__PATH + 'Bikes.csv')
        bc.load_export(TFInitializer.__PATH + 'export.csv')
        bc_df = bc.get_df()

        for idx, row in bc_df.iterrows():
            if idx in list(out_df.index):
                out_df.loc[idx]['intensity'] = row['intensity']
            else:
                out_df.loc[idx] = [numpy.nan, row['intensity'], numpy.nan, numpy.nan]

    @staticmethod
    def __InitCars(out_df):

        cc = TFCarsCreatorDaily(TFInitializer.__PATH + 'ten_minutes.csv')
        cc.load_database(TFInitializer.__PATH + 'Cars.csv')
        cc_df = cc.get_df(TFInitializer.__PATH + 'Cars.csv')

        for idx, row in cc_df.iterrows():

            if idx in list(out_df.index):
                out_df.loc[idx]['cars'] = row['intensity']
            else:
                out_df.loc[idx] = [row['intensity'], numpy.nan, numpy.nan, numpy.nan]

    @staticmethod
    def __InitWeather(out_df):

        days = pandas.to_datetime(out_df.index)
        wc = TFWUWeatherCreator(TFInitializer.__PATH + 'Weather.csv')

        for day in days:
            wc.download_weather(day)

        wc_df = wc.get_df()

        for idx, row in wc_df.iterrows():

            if idx in list(out_df.index):
                out_df.loc[idx]['temp'] = row['temp']
                out_df.loc[idx]['precip'] = row['precip']
            else:
                out_df.loc[idx] = [numpy.nan, numpy.nan, row['temp'], row['precip']]

    @staticmethod
    def __calculate_forecast():
        mc = TFModel()
        mc.create_model(TFInitializer.__PATH + 'Archive.csv')
        now = datetime.datetime.now()
        [t_temp, t_precip, da_t_temp, da_t_precip] = TFWeatherForecastGetter.Get_Forecast(now)

        t_bikes_fc = mc.get_bikes(now, t_temp, t_precip)
        t_cars_fc = mc.get_cars(now, t_temp, t_precip)

        da_t_bikes_fc = mc.get_bikes(now, da_t_temp, da_t_precip)
        da_t_cars_fc = mc.get_cars(now, da_t_temp, da_t_precip)

        json_data = json.dumps({'cars_tomorrow': t_cars_fc, 'cars_day_after_tomorrow': da_t_cars_fc,
                                'bikes_tomorrow': t_bikes_fc, 'bikes_day_after_tomorrow': da_t_bikes_fc})

        with open(TFInitializer.__PATH + 'forecaster.json', 'w', encoding='utf-8') as outfile:
            json.dump(json_data, outfile)

        if Path(TFInitializer.__PATH + 'ForecastArchive.csv').is_file():
            out_df = pandas.read_csv(TFInitializer.__PATH + 'ForecastArchive.csv', index_col='date')
        else:
            out_df = pandas.DataFrame(columns=ForecastArchiveRow._fields)
            out_df.set_index('date')
            del out_df['date']

        out_df.loc[now.strftime('%Y-%m-%d')] = [t_cars_fc, t_bikes_fc]
        new_index = [now.strftime('%Y-%m-%d')] + [ind for ind in out_df.index if ind != now.strftime('%Y-%m-%d')]
        out_df = out_df.reindex(index=new_index)
        out_df['date'] = out_df.index

        out_df.to_csv(TFInitializer.__PATH + 'ForecastArchive.csv', index=False)

#logging.basicConfig(stream=sys.stdout, level=logging.INFO)
#ac = TFArchiveCreator('/home/konrad/TrafficForecaster_DB/Archive.csv')
#TFInitializer.Init(ac)