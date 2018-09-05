from flask import Flask, render_template, request
from ResponseDispatcher import ResponseDispatcher
from apscheduler.schedulers.blocking import BlockingScheduler
import os
from TFTask.TFTaskScheduler import TFTaskScheduler
from TFCarsGetter.TFCarsGetter import TFCarsGetter
from TFArchiveGetter.TFArchiveCreator import TFArchiveCreator
from TFInitializer.TFInitializer import TFInitializer
from TFUpdateTask.TFUpdateTask import TFUpdateTask

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cgi-bin/<path:path>')
def cgi_bin(path):
	if 'api' in path:
   		return ResponseDispatcher.Dispatch(path)

def ten_min_job():
    cgt.task()


def daily_job():
    ut.task()

ResponseDispatcher.Set_path('./database/')

ut = TFUpdateTask('./database/')
cgt = TFCarsGetter('./database/' , 'ten_minutes')


sched = BlockingScheduler()
sched.add_job(daily_job, trigger='cron', hour='3', minute='1')
sched.add_job(ten_min_job, trigger='interval', minutes=10)

ac = TFArchiveCreator('./database/' + 'Archive.csv')
TFInitializer.Init(ac, './database/')

sched.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
