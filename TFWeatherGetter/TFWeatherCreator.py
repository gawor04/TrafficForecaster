import logging
import datetime
import time
import requests
import re
import pandas
from collections import namedtuple
import sys

class TFWeatherCreator:

    __METEO_ZIKIT = 'http://83.14.235.178/zbiorcza_m.php?czas='
    Weather = namedtuple('Weather', 'temp precip year month day hour minute')
    DailyWeather = namedtuple('DailyWeather', 'temp precip year month day')

    def __init__(self):

        logging.debug('New WeatherCreator')

    def setHoursQuantum(self, everyXminutes):

        self.everyXminutes = everyXminutes
        logging.debug('WeatherCreator everyXminutes:' + str(everyXminutes))

    def setDaysRange(self, yearStart, monthStart, dayStart, yearStop, monthStop, dayStop):

        self.dateStart = datetime.datetime(yearStart, monthStart, dayStart)
        self.dateStop  = datetime.datetime(yearStop, monthStop, dayStop)

        logging.debug('New WeatherCreator dateStart:' + self.dateStart.strftime("%Y-%m-%d %H:%M:%S"))
        logging.debug('New WeatherCreator dateStop:' + self.dateStop.strftime("%Y-%m-%d %H:%M:%S"))

        now = datetime.datetime.now()
        now = datetime.datetime(now.year, now.month, now.day)

        if self.dateStart >= now or self.dateStop >= now:

            raise ValueError('Wrong start or stop day')

    def setOutputFile(self, outFile):

        self.outFile = outFile
        logging.debug('New WeatherCreator outFile:' + outFile)

    def getAndSaveDataBase(self):

        datesRange = [self.dateStart + datetime.timedelta(days=x) for x in range(0, (self.dateStop - self.dateStart).days)]
        weathers = []

        for date in datesRange:

            weathers += self.__getWeather(date)

        df = pandas.DataFrame(weathers, columns=weathers[0]._fields)
        df.to_csv(self.outFile, encoding='ISO-8859-2', index=False)

    def createDaily(self, inFile, outFile, startHour, stopHour):

        self.createDailyDf(inFile, startHour, stopHour).to_csv(outFile, encoding='ISO-8859-2', index=False)

    def createDailyDf(self, inFile, startHour, stopHour):
        logging.debug('createDaily inFile: ' + inFile + ' outFile: ' + outFile)
        logging.debug('createDaily startHour: ' + str(startHour) + ' stopHour: ' + str(stopHour))

        try:
            df = pandas.read_csv(inFile, sep=',')

        except:
            print(inFile + " ERROR")
            df = None

        startDay = datetime.datetime(year=int(df.iloc[0].year), month=int(df.iloc[0].month), day=int(df.iloc[0].day))
        stopDay = datetime.datetime(year=int(df.iloc[-1].year), month=int(df.iloc[-1].month), day=int(df.iloc[-1].day))

        datesRange = [startDay + datetime.timedelta(days=x) for x in range(0, (stopDay - startDay).days)]
        dailyWeatherList = []

        for date in datesRange:

            dayRows = df[(df['year'] == date.year) & (df['month'] == date.month) & (df['day'] == date.day) &
                         (df['hour'] >= startHour) & (df['hour'] <= stopHour)]

            dailyWeatherList.append(TFWeatherCreator.DailyWeather(dayRows['temp'].mean(), dayRows['precip'].mean(),
                                                                  date.year, date.month, date.day))

        return pandas.DataFrame(dailyWeatherList, columns=dailyWeatherList[0]._fields)




    def __getWeather(self, date):

        date.replace(hour=0, minute=0)
        day = date.day
        weatherList = []

        while day == date.day:

            r = requests.get(self.__METEO_ZIKIT + str(int(time.mktime(date.timetuple()))))

            while (r.status_code != 200):
                r = requests.get(self.__METEO_ZIKIT + str(int(time.mktime(date.timetuple()))))
                logging.warning("http get status code: " + str())
                print(r.status_code)

            htmlContent = str(r.content, 'ISO-8859-2', errors='replace')
            retVal = self.__parseHTML(htmlContent)

            logging.info("getWeather day: " + date.strftime("%Y-%m-%d %H:%M:%S"))
            logging.info("getWeather precip: " + str(retVal[0]) + " temp: " + str(retVal[1]))

            weatherList.append(TFWeatherCreator.Weather(retVal[1], retVal[0], date.year, date.month, date.day, date.hour, date.minute))
            date = date + datetime.timedelta(minutes=self.everyXminutes)

        return weatherList

    def __parseHTML(self, html):
        table = re.findall(r'<tr.*?>(.*?)</tr>', html)

        precip = 0.0
        temp = 0.0

        if(len(table) > 0):
            mean_row = table[-2]
            mean_row_values = re.findall(r'<td.*?>(.*?)</td>', mean_row)

            if(len(mean_row_values) >= 8):
                mean_precip_cell = mean_row_values[7]
                mean_temp_cell = mean_row_values[3]

                mean_precip_value = re.findall(r'\d+\.\d+', mean_precip_cell)
                mean_temp_value = re.findall(r'[-+]?\d+\.\d+', mean_temp_cell)

                if(len(mean_precip_value) > 0):
                    precip = float(mean_precip_value[0])

                if (len(mean_temp_value) > 0):
                    temp = float(mean_temp_value[0])

        return [precip, temp]


#logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

#arg_len = len(sys.argv)

#if(arg_len != 8):
#    print("Wrong arguments number")
#    exit()

#ofile = sys.argv[1]
#startYear = int(sys.argv[2])
#startMonth = int(sys.argv[3])
#startDay = int(sys.argv[4])
#stopYear = int(sys.argv[5])
#stopMonth = int(sys.argv[6])
#stopDay = int(sys.argv[7])


#wc = WeatherCreator()
#wc.setDaysRange(startYear, startMonth, startDay, stopYear, stopMonth, stopDay)
#wc.setHoursQuantum(30)
#wc.setOutputFile(ofile)
#wc.getAndSaveDataBase()

#wc = TFWeatherCreator()
#wc.createDaily('weather.csv', 'dailyWeather.csv', 8, 10)

