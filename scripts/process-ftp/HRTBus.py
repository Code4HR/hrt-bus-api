from datetime import datetime

class Checkin:
	def __init__(self, data, year):
		parts = data.split(',')
		
		# checkin time
		self.time = datetime.strptime(parts[0] + ' ' + parts[1] + '/' + year, "%H:%M:%S %m/%d/%Y")
		
		# bus id
		self.busId = int(parts[2])
		
		# location
		if parts[4] == 'V':
			location = parts[3].split('/')
			self.lat = location[0][:2] + '.' + location[0][2:]
			self.long = location[1][:3] + '.' + location[1][3:]
		
		# adherence
		if parts[6] == 'V':
			self.adherence = int(parts[5])
			
		if len(parts) == 10:
			self.route = int(parts[7])
			self.direction = int(parts[8])
			self.stop = int(parts[9])