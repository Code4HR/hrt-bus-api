from datetime import datetime, timedelta
from pymongo import Connection

class HRTDatabase:
	def __init__(self, uri):
		self.client = Connection(uri)
		self.database = self.client.hrt

	def removeOldGTFS(self, date):
		collectionName = 'gtfs_' + date.strftime('%Y%m%d')
		for collection in self.database.collection_names():
			if collection.startswith('gtfs') and collection != collectionName:
				self.database.drop_collection(collection)
	
	def insertGTFS(self, data, date):
		collectionName = 'gtfs_' + date.strftime('%Y%m%d')
		if len(data) > 0:
			self.database[collectionName].remove()
			self.database[collectionName].insert(data)
	
	def insertStops(self, data):
		self.database['stops'].remove()
		self.database['stops'].insert(data)
	
	def insertRoutes(self, data):
		self.database['routes'].remove()
		self.database['routes'].insert(data)
	
