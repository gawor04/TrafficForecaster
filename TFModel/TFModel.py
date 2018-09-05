import pandas
import datetime
import scipy.linalg
import numpy
import matplotlib.pyplot as plt
import sys
from sklearn.metrics import mean_absolute_error

class TFModel:

    def create_model(self, arch_file):

        out_df = pandas.read_csv(arch_file, index_col='date')
        out_df.index = pandas.to_datetime(out_df.index)

        not_holiday_idxs = filter(self.__isNotHoliday, out_df.index)
        holiday_idxs = filter(self.__isHoliday, out_df.index)

        not_holiday_df = out_df[out_df.index.isin(not_holiday_idxs)]
        holiday_df = out_df[out_df.index.isin(holiday_idxs)]

        self.__cars_holi_model = self.__get_model(self.__get_cars_df(holiday_df))
        self.__cars_normal_model = self.__get_model(self.__get_cars_df(not_holiday_df))

        self.__bikes_holi_model = self.__get_model(self.__get_bikes_df(holiday_df))
        self.__bikes_normal_model = self.__get_model(self.__get_bikes_df(not_holiday_df))

    def get_bikes(self, day, temp, precip):

        if self.__isHoliday(day):
            return int(numpy.dot(numpy.c_[numpy.ones(1), precip, temp, precip * temp, precip ** 2, temp ** 2],
                             self.__bikes_holi_model)[0])
        else:
            return int(numpy.dot(numpy.c_[numpy.ones(1), precip, temp, precip * temp, precip ** 2, temp ** 2],
                             self.__bikes_normal_model)[0])

    def get_cars(self, day, temp, precip):

        if self.__isHoliday(day):
            return int(numpy.dot(numpy.c_[numpy.ones(1), precip, temp, precip * temp, precip ** 2, temp ** 2],
                             self.__cars_holi_model)[0])
        else:
            return int(numpy.dot(numpy.c_[numpy.ones(1), precip, temp, precip * temp, precip ** 2, temp ** 2],
                             self.__cars_normal_model)[0])

    def __get_cars_df(self, archive_df):

        cars_df = archive_df[['cars', 'temp', 'precip']]
        cars_df = cars_df.dropna()
        return cars_df

    def __get_bikes_df(self, archive_df):

        bikes_df = archive_df[['bikes', 'temp', 'precip']]
        bikes_df = bikes_df.dropna()
        return bikes_df

    def __get_model(self, intensity_df):

        data = intensity_df.values
        data[:, [0, 2]] = data[:, [2, 0]]

        A = numpy.c_[numpy.ones(data.shape[0]), data[:, :2], numpy.prod(data[:, :2], axis=1), data[:, :2] ** 2]
        C, _, _, _ = scipy.linalg.lstsq(A, data[:, 2])

        return C

    def __isNotHoliday(self, day):
        return not self.__isHoliday(day)

    def __isHoliday(self, day):

        # saturnday or sunday
        if day.isoweekday() == 6 or day.isoweekday() == 7:
            return True
        # new year
        if day.month == 1 and day.day == 1:
            return True
        # Three Kings Day
        if day.month == 1 and day.day == 6:
            return True
        # Labour Day
        if day.month == 5 and day.day == 1:
            return True
        # Constitution Day
        if day.month == 5 and day.day == 3:
            return True
        # Assumption of the Blessed Virgin Mary
        if day.month == 8 and day.day == 15:
            return True
        # All Saints' Day
        if day.month == 11 and day.day == 1:
            return True
        # Independence day
        if day.month == 11 and day.day == 11:
            return True
        # Christmas Day
        if day.month == 12 and day.day == 25:
            return True
        # Second Day of Christmas
        if day.month == 12 and day.day == 26:
            return True

        a = day.year % 19
        b = day.year % 4
        c = day.year % 7
        d = (a * 19 + 24) % 30
        e = (2 * b + 4 * c + 6 * d + 5) % 7
        if d == 29 and e == 6:
            d -= 7
        if d == 28 and e == 6 and a > 10:
            d -= 7

        easter = datetime.datetime(day.year, 3, 22)
        easter += datetime.timedelta(days=(d + e))

        # Easter
        if (day + datetime.timedelta(-1)) == easter:
            return True
        # Corpus Christi
        if (day + datetime.timedelta(-60)) == easter:
            return True

        return False

#tmodel = TFModel()
#tmodel.create_model('../TFArchiveGetter/Archive.csv')
#print(tmodel.get_cars(datetime.datetime.now(), 23.0, 36.0))
#print(tmodel.get_bikes(datetime.datetime.now(), 22.0, 0.5))