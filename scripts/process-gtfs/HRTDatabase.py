from datetime import datetime, timedelta
from pymongo import Connection

class HRTDatabase:
	def __init__(self, uri):
		self.client = Connection(uri)
		self.database = self.client.hrt

	def removeOldGTFS(self, date):
		print "Removing Old GTFS Data"
		collectionPrefix = self.genCollectionName('', date)
		for collection in self.database.collection_names():
			if collection.find('_') != -1 and (not collection.endswith(collectionPrefix)):
				self.database.drop_collection(collection)
	
	def insertGTFS(self, data, date):
		self.insertData(self.genCollectionName('gtfs_', date), data)
	
	def insertStops(self, data, date):
		self.insertData(self.genCollectionName('stops_', date), data)
	
	def insertRoutes(self, data, date):
		self.insertData(self.genCollectionName('routes_', date), data)
	
	def genCollectionName(self, prefix, date):
		return prefix + date.strftime('%Y%m%d')
	
	def insertData(self, collectionName, data):
		if len(data) > 0:
			self.database[collectionName].remove()
			self.database[collectionName].insert(data)
	
