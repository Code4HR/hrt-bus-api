from ftplib import FTP
from datetime import datetime, timedelta
from HRTBus import Checkin
from HRTDatabase import HRTDatabase
import config
		
def process(text):
	global numSkipped
	global skip
	
	if text.strip():
		try:
			bc = Checkin(text, str(curTime.year))
			
			if not skip:
				checkinDocs.append(bc.__dict__)
				if hasattr(bc, 'route'):
					busRouteMappings[bc.busId] = (bc.route, bc.time)
			elif bc.time > lastTime or (bc.time == lastTime and bc.busId not in lastBuses):
				skip = False
				checkinDocs.append(bc.__dict__)
				if hasattr(bc, 'route'):
					busRouteMappings[bc.busId] = (bc.route, bc.time)
			else:
				numSkipped += 1
				
		except ValueError:
			#print "Bad data: " + text
			pass # does nothing

c = config.load()

# ftp data doesn't include the year, so get the current time (EST)
curTime = datetime.utcnow() + timedelta(hours=-5)
oldTime = curTime + timedelta(minutes=-30)

db = HRTDatabase(c["db_uri"])

busRouteMappings = db.getBusRouteMappings()
print str(len(busRouteMappings)) + " Bus Route Mappings read from db"

checkinDocs = []

# get last checkin
lastCheckinInfo = db.getLastCheckinSummary()
skip = False
if lastCheckinInfo is not None:
	lastTime = lastCheckinInfo[0]
	lastBuses = lastCheckinInfo[1]
	skip = True

numSkipped = 0

# get the bus checkin data and process it
ftp = FTP('216.54.15.3')
ftp.login()
ftp.cwd('Anrd')
ftp.retrlines('RETR hrtrtf.txt', process)

busRouteMapArray = []
for key, value in busRouteMappings.items():
	busRouteMapArray.append({"busId":key, "route": value[0], "time": value[1]})
db.setBusRouteMappings(busRouteMapArray)
print str(len(busRouteMappings)) + " Bus Route Mappings inserted into db"

print "Skipped " + str(numSkipped)

db.updateCheckins(checkinDocs)
print "Added " + str(len(checkinDocs))