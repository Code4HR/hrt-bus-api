import json
from StringIO import StringIO
from urllib import urlopen
from zipfile import ZipFile

feedUrl = "http://www.gtfs-data-exchange.com/api/agency?agency=hampton-roads-transit-hrt"
fileUrl = json.loads(urlopen(feedUrl).read())['data']['datafiles'][0]['file_url']
zipFile = ZipFile(StringIO(urlopen(fileUrl).read()))

calLines = zipFile.open("calendar.txt").read().splitlines()
for line in calLines:
	print line

stopTimesLines = zipFile.open("stop_times.txt").read().splitlines()
for idx, line in enumerate(stopTimesLines):
    print idx, line