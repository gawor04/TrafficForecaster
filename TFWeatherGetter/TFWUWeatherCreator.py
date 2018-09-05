from pathlib import Path
import pandas
import datetime
import requests
import logging
import json

import sys
sys.path.append('../')
from TFTypes.TFTypes import WeatherRow

class TFWUWeatherCreator:

    __KEY = '08704a121bcb1363'
    __WU_ADDRESS = 'http://api.wunderground.com/api/'

    def __init__(self, output_file):

        self.__output_file = output_file
        self.__logger = logging.getLogger('TFWUWeatherCreator')

    def download_weather(self, day):

        if Path(self.__output_file).is_file():
            out_df = pandas.read_csv(self.__output_file, index_col='date')

            if not out_df[out_df.index.str.contains(day.strftime('%Y-%m-%d'))].empty:
                self.__logger.warning('database already has that item: ' + str(day))

                return [out_df.loc[day.strftime('%Y-%m-%d')]['temp'], out_df.loc[day.strftime('%Y-%m-%d')]['precip']]
        else:
            out_df = pandas.DataFrame(columns=WeatherRow._fields)
            out_df.set_index('date')
            del out_df['date']

        weather = self.__get_weather(day)

        if weather is not None:
            out_df.loc[day.strftime('%Y-%m-%d')] = weather

            new_index = [day.strftime('%Y-%m-%d')] + [ind for ind in out_df.index if ind != day.strftime('%Y-%m-%d')]
            out_df = out_df.reindex(index=new_index)

            out_df['date'] = out_df.index
            out_df.to_csv(self.__output_file, columns=WeatherRow._fields, index=False)

            return weather
        else:
            return None

    def get_df(self):
        return pandas.read_csv(self.__output_file, index_col='date')

    def __get_weather(self, day):

        self.__logger.info('new day: ' + str(day))

        json_date = day.strftime("%Y%m%d")
        history = '/history_' + json_date + '/lang:PL/q/PL/Kraków.json'

        r = requests.get(self.__WU_ADDRESS + self.__KEY + history)

        while r.status_code != 200:
            self.__logger.warning('GET: status code: ' + str(r.status_code))
            r = requests.get(self.__WU_ADDRESS + self.__KEY + history)

        try:
            json_resp = r.json()
            js = json_resp['history']['dailysummary']

            precip = js[0]['precipm']
            temp = js[0]['meantempm']
            return [temp, precip]

        except:

            self.__logger.error('JSON parse error')
            return None