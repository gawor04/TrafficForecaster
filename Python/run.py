from TFTask.TFTaskScheduler import TFTaskScheduler
from TFCarsGetter.TFCarsGetter import TFCarsGetter
from TFArchiveGetter.TFArchiveCreator import TFArchiveCreator
from TFInitializer.TFInitializer import TFInitializer
from TFUpdateTask.TFUpdateTask import TFUpdateTask
from time import sleep
from apscheduler.schedulers.blocking import BlockingScheduler
import sys

if len(sys.argv) < 1:
    print("Wrong paramaters, sould set database path!!!")

db_path = sys.argv[1]

sched = BlockingScheduler()
ut = TFUpdateTask(db_path)
cgt = TFCarsGetter(db_path , 'ten_minutes')


def ten_min_job():
    cgt.task()


def daily_job():
    ut.task()


sched.add_job(daily_job, trigger='cron', hour='3', minute='1')
sched.add_job(ten_min_job, trigger='interval', minutes=10)

ac = TFArchiveCreator(db_path + 'Archive.csv')
TFInitializer.Init(ac, db_path)

sched.start()

while True:
    sleep(1)
