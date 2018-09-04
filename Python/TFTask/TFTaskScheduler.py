import logging
from apscheduler.schedulers.background import BackgroundScheduler
import time

class TFTaskScheduler:
    __taskList = []
    __logger = logging.getLogger(__name__)

    def addTask(self, task):
        self.__logger.debug("new TFTask in TFTaskScheduler name: " + task.name)
        self.__taskList.append(task)

    def run(self):
        scheduler = BackgroundScheduler()

        for task in self.__taskList:

            if task.interval_min > 0:

                scheduler.add_job(task.task, 'interval', minutes=task.interval_min)

            elif task.interval_h > 0:

                scheduler.add_job(task.task, 'interval', hours=task.interval_h)

            else:

                self.warning("task name: " + task.name + "no interval set")

        if len(self.__taskList) > 0:
            self.__logger.debug("TFTaskScheduler started!")
            scheduler.start()

        while True:
            time.sleep(1)
            self.__logger.debug("TFTaskScheduler is alive")
