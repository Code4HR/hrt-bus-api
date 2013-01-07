from datetime import datetime, timedelta
from pymongo import Connection

class HRTDatabase:
	def __init__(self, uri):
		self.client = Connection(uri)
		self.database = self.client.hrt

	def insertGTFS(self, data, date):
		collectionName = 'gtfs_' + date.strftime('%Y%m%d')
		if len(data) > 0:
			self.database[collectionName].remove()
			self.database[collectionName].insert(data)
	

