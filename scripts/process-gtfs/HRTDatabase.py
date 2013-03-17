from datetime import datetime, timedelta
from pymongo import Connection, GEO2D

class HRTDatabase:
	def __init__(self, uri, db):
		self.client = Connection(uri)
		self.database = self.client[db]

	def removeOldGTFS(self, date):
		print "Removing Old GTFS Data"
		collectionPrefix = self.genCollectionName('', date)
		for collection in self.database.collection_names():
			if collection.find('_') != -1 and (not collection.endswith(collectionPrefix)):
				self.database.drop_collection(collection)
	
	def insertGTFS(self, data, date):
		self.insertData(self.genCollectionName('gtfs_', date), data)
	
	def insertStops(self, data, date):
		collectionName = self.genCollectionName('stops_', date)
		self.insertData(collectionName, data)
		self.database[collectionName].ensure_index( [('location', GEO2D)] )
	
	def insertRoutes(self, data, date):
		self.insertData(self.genCollectionName('routes_', date), data)
	
	def genCollectionName(self, prefix, date):
		return prefix + date.strftime('%Y%m%d')
	
	def insertData(self, collectionName, data):
		if len(data) > 0:
			self.database[collectionName].remove()
			self.database[collectionName].insert(data)
	
