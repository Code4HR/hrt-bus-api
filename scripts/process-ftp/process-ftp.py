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
	
	try:
		checkin = Checkin(text, str(curTime.year))
	except ValueError:
		return
	
	if checkinProcessed(checkin):
		return
	
	checkinDocs.append(checkin.__dict__)
	if hasattr(checkin, 'route'):
		busRouteMappings[checkin.busId] = (checkin.route, checkin.time)

c = config.load()
db = HRTDatabase(c["db_uri"])
curTime = datetime.utcnow() + timedelta(hours=-5)

busRouteMappings = db.getBusRouteMappings()
print "{0} Bus Route Mappings read from db".format(len(busRouteMappings))

lastCheckins = db.getLastCheckinSummary()
checkinDocs = []

ftp = FTP('216.54.15.3')
ftp.login()
ftp.cwd('Anrd')
ftp.retrlines('RETR hrtrtf.txt', process)

busRouteMapArray = []
for key, value in busRouteMappings.items():
	busRouteMapArray.append({"busId":key, "route": value[0], "time": value[1]})
db.setBusRouteMappings(busRouteMapArray)
print "{0} Bus Route Mappings inserted into db".format(len(busRouteMappings))

db.updateCheckins(checkinDocs)
print "Added " + str(len(checkinDocs))