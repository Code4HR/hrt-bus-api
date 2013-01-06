import json
from StringIO import StringIO
from urllib import urlopen
from zipfile import ZipFile
from csv import DictReader
from datetime import datetime, timedelta

feedUrl = "http://www.gtfs-data-exchange.com/api/agency?agency=hampton-roads-transit-hrt"
fileUrl = json.loads(urlopen(feedUrl).read())['data']['datafiles'][0]['file_url']
zipFile = ZipFile(StringIO(urlopen(fileUrl).read()))

days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
curDate = (datetime.utcnow() + timedelta(hours=-5)).date()
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

activeTrips = []
activeTripIds = []
trips = DictReader(zipFile.open("trips.txt"))
for row in trips:
	if row['service_id'] in activeServiceIds:
		activeTrips.append(row)
		activeTripIds.append(row['trip_id'])
print str(len(activeTrips)) + " active trips"

activeStopTimes = []
stopTimes = DictReader(zipFile.open("stop_times.txt"))
for row in stopTimes:
	if row['trip_id'] in activeTripIds:
		activeStopTimes.append(row)
print str(len(activeStopTimes)) + " active stop times"