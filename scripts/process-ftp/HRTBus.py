import pytz
from datetime import datetime, timedelta

class Checkin:
	def __init__(self, data, year):
		parts = data.split(',')
		
		# checkin time
		# bug here if the file contains checkins from both 12/31/N and 1/1/N+1
		local = pytz.timezone('US/Eastern')
		naive = datetime.strptime(parts[0] + ' ' + parts[1] + '/' + year, "%H:%M:%S %m/%d/%Y")
		local_dt = local.localize(naive, is_dst=None)
		self.time = local_dt.astimezone(pytz.utc)
		
		# bus id
		self.busId = int(parts[2])
		
		# location
		if parts[4] == 'V':
			location = parts[3].split('/')
			lat = float(location[0][:2] + '.' + location[0][2:])
			lon = float(location[1][:3] + '.' + location[1][3:])
			self.location = [lon, lat]
		
		# adherence
		if parts[6] == 'V':
			self.adherence = int(parts[5])
			
		if len(parts) == 10:
			self.routeId = int(parts[7])
			self.direction = int(parts[8]) - 1
			self.stopId = int(parts[9])