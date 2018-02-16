import ftp
import gtfs
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

#@sched.scheduled_job('interval', minutes=1)
#def ftp_job():
#    print 'Running FTP Job
#    ftp.process({}, None)
#    print 'FTP Job Complete'

@sched.scheduled_job('cron', hour=19, minute=30)
def gtfs_job():
    print  'Running GTFS Job'
    gtfs.process({}, None)
    print 'GTFS Job Complete'

sched.start()