import logging
import datetime
from TFWeatherGetter.TFWeatherCreator import TFWeatherCreator
from TFTask.TFTask import TFTask

class TFWeatherGetter(TFTask):
    __logger = logging.getLogger(__name__)
    __MIN_QUANTUM = 30

    def __init__(self, outfile, name, interval_min=0, interval_h=0):
        TFTask.__init__(self, name, interval_min, interval_h)
        self.wc = TFWeatherCreator()
        self.wc.setHoursQuantum(self.__MIN_QUANTUM)
        self.wc.setOutputFile(outfile)

    def task(self):
        now = datetime.datetime.now()
        prev = now - datetime.timedelta(days=1)
        self.wc.setDaysRange(prev.year, prev.month, prev.day, prev.year, prev.month, prev.day)
        self.wc.getAndSaveDataBase()
