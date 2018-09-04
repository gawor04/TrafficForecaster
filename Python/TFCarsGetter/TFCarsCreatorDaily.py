import pandas
import datetime
import logging
from pathlib import Path
import numpy
import sys
sys.path.append('../')
from TFTypes.TFTypes import IntensityRow

class TFCarsCreatorDaily:

    __APPROVED_STATION_LST = ['Rondo Kocmyrzowskie:Nowa Huta:lewy',
                              'Sawickiego/Medweckiego:Podgórze:lewy',
                              'Sawickiego/Medweckiego:Podgórze:prawy',
                              'Skotnicka/Babińskiego:Centrum:pomiar',
                              'Wielicka/Nowosądecka:Centrum:lewy',
                              'Wielicka/Nowosądecka:Centrum:prawy',
                              'Wielicka/Nowosądecka:Centrum:środkowy',
                              'Wielicka/Nowosądecka:Wieliczka:lewy',
                              'Wielicka/Nowosądecka:Wieliczka:prawy',
                              'Wielicka/Nowosądecka:Wieliczka:środkowy']

    __DAILY_MIN_VALUES = 18

    def __init__(self, input_file):

        self.__logger = logging.getLogger(__name__)
        self.__input_file = input_file

    def create_daily(self, day, out_file):

        if Path(out_file).is_file():
            logging.info(out_file + ' exists')
            out_df = pandas.read_csv(out_file, index_col='date')

            if not out_df[out_df.index.str.contains(day.strftime('%Y-%m-%d'))].empty:
                logging.info('out file already contains that day')
                return out_df.loc[day.strftime('%Y-%m-%d')]['intensity']
        else:
            out_df = pandas.DataFrame(columns=IntensityRow._fields)
            out_df.set_index('date')
            del out_df['date']

        in_df = pandas.read_csv(self.__input_file, error_bad_lines=False,
                             encoding='ISO-8859-2', index_col='date')

        day_df = self.__get_day_df(in_df, day)
        if day_df is not None and self.__filter_columns(day_df):

            self.__calculate_unknown_values(day_df)
            day_sum = day_df.values.sum()

            out_df.loc[day.strftime('%Y-%m-%d')] = day_sum
            new_index = [day.strftime('%Y-%m-%d')] + [ind for ind in out_df.index if ind != day.strftime('%Y-%m-%d')]
            out_df = out_df.reindex(index=new_index)
            out_df['date'] = out_df.index
            out_df.to_csv(out_file, encoding='ISO-8859-2', index=False)

            return day_sum
        else:
            return numpy.nan

    def load_database(self, out_file):

        in_df = pandas.read_csv(self.__input_file, error_bad_lines=False,
                                encoding='ISO-8859-2', index_col='date')

        days = pandas.to_datetime(in_df.index)
        new = max(days)
        old = min(days)
        date_list = [old + datetime.timedelta(days=x) for x in range(0, (new - old).days)]

        for date in date_list:
            self.__logger.info('new day: ' + str(date))
            self.create_daily(date, out_file)

    def get_df(self, out_file):

        return pandas.read_csv(out_file, error_bad_lines=False,
                                encoding='ISO-8859-2', index_col='date')


    def __get_day_df(self, ten_min_df, date):

        day_df = ten_min_df[ten_min_df.index.str.contains(date.strftime('%Y-%m-%d'))]

        if len(day_df) < self.__DAILY_MIN_VALUES:
            self.__logger.warning('too little values, no day in database: ' + str(date))
            return None

        return day_df

    def __filter_columns(self, day_df):

        location_list = list(day_df.columns)

        for location in location_list:
            if location not in self.__APPROVED_STATION_LST:
                del day_df[location]

        if len(list(day_df)) == len(self.__APPROVED_STATION_LST):
            return True
        else:
            self.__logger.warning('too little stations in database')
            return False

    def __calculate_unknown_values(self, day_df):

        location_list = list(day_df.columns)

        for location in location_list:
            location_series = day_df[location]
 #           location_series = location_series.replace('0', 'NaN')
            location_series = location_series.replace('-', 'NaN')
            location_series = location_series.astype('float64')
            location_series = location_series.interpolate()
            day_df[location] = location_series

#logging.basicConfig(filename='example.log',level=logging.INFO)
#cc = TFCarsCreatorDaily('ten_minutes.csv')
#cc.create_daily(datetime.datetime(year=2018, month= 6, day=12), 'out.csv')