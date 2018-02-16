import gtfs
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

#@sched.scheduled_job('interval', minutes=3)
#def timed_job():
#    print('This job is run every three minutes.')

@sched.scheduled_job('cron', hour=14)
def gtfs_job():
    print  'Running GTFS Job'
    gtfs.process({}, None)

sched.start()