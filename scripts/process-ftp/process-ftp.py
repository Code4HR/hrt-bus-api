from ftplib import FTP
from datetime import datetime, timedelta
from HRTBus import Checkin
from HRTDatabase import HRTDatabase
import config

def checkinProcessed(checkin):
	if lastCheckins is None:
		return False
	if checkin.time == lastCheckins["time"]:
		return checkin.busId in lastCheckins["busIds"]
	return checkin.time < lastCheckins["time"]

def process(text):
	if not text.strip():
		return
	
	stats['lines'] += 1
	
	try:
		checkin = Checkin(text, str(curTime.year))
	except ValueError:
		stats['invalid'] += 1
		return
	
	if hasattr(checkin, 'route'):
		print checkin.__dict__
			
	if checkinProcessed(checkin):
		return
	
	stats['processed'] += 1
	
	if hasattr(checkin, 'route'):
		busRouteMappings[checkin.busId] = (checkin.route, checkin.time)
		stats['hadRoute'] += 1
	elif checkin.busId in busRouteMappings:
		checkin.route = busRouteMappings[checkin.busId][0]
		stats['foundRoute'] += 1
	checkinDocs.append(checkin.__dict__)

c = config.load()
db = HRTDatabase(c["db_uri"])
curTime = datetime.utcnow() + timedelta(hours=-5)

busRouteMappings = db.getBusRouteMappings()
print "Read {0} Bus Route Mappings".format(len(busRouteMappings))

lastCheckins = db.getLastCheckinSummary()
checkinDocs = []
stats = {'lines': 0, 'invalid': 0, 'processed': 0, 'hadRoute': 0, 'foundRoute': 0}

ftp = FTP('216.54.15.3')
ftp.login()
ftp.cwd('Anrd')
ftp.retrlines('RETR hrtrtf.txt', process)

busRouteMapArray = []
for key, value in busRouteMappings.items():
	busRouteMapArray.append({"busId":key, "route": value[0], "time": value[1]})
db.setBusRouteMappings(busRouteMapArray)
print "Inserted {0} Bus Route Mappings".format(len(busRouteMappings))

db.updateCheckins(checkinDocs)
print "Added {0} Checkins".format(len(checkinDocs))

for key, value in stats.iteritems():
	print "{0} {1}".format(key, value)