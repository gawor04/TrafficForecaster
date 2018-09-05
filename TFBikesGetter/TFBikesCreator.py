import requests
import re
import logging
import pandas
from datetime import datetime, timedelta
from pathlib import Path
import sys
sys.path.append('../')
from TFTypes.TFTypes import IntensityRow

class TFBikesCreator:

    __STATION_IDS = ['100034391', '100034392', '100034393',
                     '100034394', '100034395', '100041257',
                     '100041258', '100041259', '100041869']
    __WWW_PREFIX = 'https://eco-public.com/eco-widget/last_day.jsp?id='
    __REG_EX = r'<p id="comptages">(.*?)</p>'
    __ALL_LOC = ["Bulwary", "Dworzec Główny", "Kotlarska", "Mogilska",
                 "Monte Cassino", "Smoleńsk", "Tyniecka", "Wadowicka",
                 "Wielicka"]

    def __init__(self, output_file):

        self.__output_file = output_file
        self.__logger = logging.getLogger('TFBikesCreator')

    def download_last_day(self, day):

        if Path(self.__output_file).is_file():
            out_df = pandas.read_csv(self.__output_file, index_col='date')

            if not out_df[out_df.index.str.contains(day.strftime('%Y-%m-%d'))].empty:
                logging.warning('database already has that item: ' + str(day))
                return out_df.loc[day.strftime('%Y-%m-%d')]['intensity']
        else:
            out_df = pandas.DataFrame(columns=IntensityRow._fields)
            out_df.set_index('date')
            del out_df['date']

        bikes_intensity = self.__get_bikes_intensity()

        if bikes_intensity is 0:
            return None

        out_df.loc[day.strftime('%Y-%m-%d')] = bikes_intensity
        new_index = [day.strftime('%Y-%m-%d')] + [ind for ind in out_df.index if ind != day.strftime('%Y-%m-%d')]
        out_df = out_df.reindex(index=new_index)
        out_df['date'] = out_df.index
        out_df.to_csv(self.__output_file, index=False)

        return bikes_intensity

    def get_df(self):

        return pandas.read_csv(self.__output_file, index_col='date')

    def load_export(self, export_file):

        is_new_out_file = False

        if Path(self.__output_file).is_file():
            out_df = pandas.read_csv(self.__output_file, index_col='date')

        else:
            out_df = pandas.DataFrame(columns=IntensityRow._fields)
            out_df.set_index('date')
            del out_df['date']
            is_new_out_file = True

        if not Path(export_file).is_file():
            self.__logger.error(export_file + ' not found')
            return

        exp_df = pandas.read_csv(export_file, index_col='Data')

        loc_list = list(exp_df.columns)

        for loc in loc_list:
            if loc not in self.__ALL_LOC:
                del exp_df[loc]

        exp_df = exp_df.dropna()

        for i, row in exp_df.iterrows():

            idx_date = datetime.strptime(i, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')

            if is_new_out_file:
                out_df.loc[idx_date] = row.sum()
            else:
                if out_df[out_df.index.str.contains(idx_date)].empty:
                    out_df.loc[idx_date] = row.sum()
                else:
                    logging.warning('database already has that item: ' + idx_date)

        out_df['date'] = out_df.index
        out_df.to_csv(self.__output_file, columns=IntensityRow._fields, index=False)

    def __get_bikes_intensity(self):

        bikes_intensity = 0

        for station in self.__STATION_IDS:

            r = requests.get(self.__WWW_PREFIX + station)

            while r.status_code is not 200:
                self.__logger('request error')

            content = str(r.content)
            reg_res = re.findall(self.__REG_EX, content)

            if len(reg_res) > 0:
                reg_res[0] = reg_res[0].replace('\\xc2\\xa0', '')
                bikes_intensity += int(reg_res[0])
            else:
                self.__logger('regex not found')
                return 0

        return bikes_intensity

#logging.basicConfig(filename='example.log',level=logging.INFO)
#cc = TFBikesCreator('out.csv')
#cc.load_export('export.csv')
#cc.download_last_day(datetime.now())


