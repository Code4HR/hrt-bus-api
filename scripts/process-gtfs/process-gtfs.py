import config
import json
import sys
from StringIO import StringIO
from urllib import urlopen
from zipfile import ZipFile
from csv import DictReader
from datetime import datetime, time, timedelta
from HRTDatabase import HRTDatabase

c = config.load()
db = HRTDatabase(c["db_uri"])
if len(sys.argv) != 2:
	db.removeOldGTFS(datetime.utcnow() + timedelta(hours=-5))

feedUrl = "http://www.gtfs-data-exchange.com/api/agency?agency=hampton-roads-transit-hrt"
fileUrl = json.loads(urlopen(feedUrl).read())['data']['datafiles'][0]['file_url']
zipFile = ZipFile(StringIO(urlopen(fileUrl).read()))

daysFromNow = 1
if len(sys.argv) == 2:
	daysFromNow = int(sys.argv[1])
days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
curDate = (datetime.utcnow() + timedelta(days=daysFromNow, hours=-5)).date()
midnight = datetime.combine(curDate, time.min)
curWeekDay = days[curDate.weekday()]
print curWeekDay + " " + str(curDate)

activeServiceIds = []
calendar = DictReader(zipFile.open("calendar.txt"))
for row in calendar:
	start = datetime.strptime(row['start_date'], "%Y%m%d").date()
	end = datetime.strptime(row['end_date'], "%Y%m%d").date()
	if curDate >= start and curDate <= end and row[curWeekDay] == '1':
		activeServiceIds.append(row['service_id'])
print activeServiceIds

activeTrips = {}
trips = DictReader(zipFile.open("trips.txt"))
for row in trips:
	if row['service_id'] in activeServiceIds:
		activeTrips[row['trip_id']] = row
print str(len(activeTrips)) + " active trips"

activeStopTimes = []
stopTimes = DictReader(zipFile.open("stop_times.txt"))
for row in stopTimes:
	if row['trip_id'] in activeTrips:
		try:
			trip = activeTrips[row['trip_id']]
			row['route_id'] = int(trip['route_id'])
			row['direction_id'] = int(trip['direction_id'])
			row['block_id'] = trip['block_id']
			row['stop_id'] = int(row['stop_id'])
			row['stop_sequence'] = int(row['stop_sequence'])
			
			arriveTime = row['arrival_time'].split(':')
			row['arrival_time'] = midnight + timedelta(hours=int(arriveTime[0])+5, minutes=int(arriveTime[1]))
			
			departTime = row['departure_time'].split(':')
			row['departure_time'] = midnight + timedelta(hours=int(departTime[0])+5, minutes=int(departTime[1]))
			
			activeStopTimes.append(row)
		except ValueError:
			pass 
print str(len(activeStopTimes)) + " active stop times"

db.insertGTFS(activeStopTimes, curDate)

stops = []
stopsReader = DictReader(zipFile.open("stops.txt"))
for row in stopsReader:
	try:
		stops.append({
			'stopId': int(row['stop_id']),
			'stopName': row['stop_name'],
			'location': [float(row['stop_lon']), float(row['stop_lat'])]
		})
	except ValueError:
		pass
print str(len(stops)) + " stops"
db.insertStops(stops, curDate)

routes = []
routesReader = DictReader(zipFile.open("routes.txt"))
for row in routesReader:
	try:
		row['route_id'] = int(row['route_id'])
		routes.append(row)
	except ValueError:
		pass
print str(len(routes)) + " routes"
db.insertRoutes(routes, curDate)