import ftp
import gtfs
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

# Process FTP every minute
@sched.scheduled_job('interval', minutes=1)
def ftp_job():
    print 'Running FTP Job'
    ftp.process({}, None)
    print 'FTP Job Complete'

# Each day at 3 AM, load schedules for the next day
@sched.scheduled_job('cron', hour=3)
def gtfs_job():
    print  'Running GTFS Job'
    gtfs.process({}, None)
    print 'GTFS Job Complete'

sched.start()
