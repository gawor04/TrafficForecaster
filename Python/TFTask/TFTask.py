import abc
import logging


class TFTask(metaclass=abc.ABCMeta):

    def __init__(self, name, interval_min=0, interval_h=0):

        logger = logging.getLogger(__name__)
        logger.debug("new TFTask name: " + str(name))

        self.name = name
        self.interval_min = interval_min
        self.interval_h = interval_h

    @abc.abstractmethod
    def task(self):
        pass
