from datetime import datetime, timedelta
from pymongo import MongoClient

class HRTDatabase:
	def __init__(self, uri):
		self.client = MongoClient(uri)
		self.database = self.client.hrt
	
	# get bus route mappings that are not more than 30 minutes old
	def getBusRouteMappings(self):
		mappings = {} 
		for mapping in self.database.busRouteMappings.find():
			if mapping["time"] > datetime.utcnow() + timedelta(hours=-5, minutes=-30):
				mappings[mapping["busId"]] = (mapping["route"], mapping["time"])
		return mappings
	
	def setBusRouteMappings(self, mappings):
		self.database.busRouteMappings.remove()
		if len(mappings) > 0:
			self.database.busRouteMappings.insert(mappings)
	
	# return the last time to the minute that a bus checked in and a list of all buses that checked in during that minute 
	def getLastCheckinSummary(self):
		if self.database.checkins.find().count() > 0:
			lastTime = self.database.checkins.find().sort("$natural", -1)[0]["time"]
			lastBuses = self.database.checkins.find({"time" : lastTime}).distinct("busId")
			return {"time": lastTime, "busIds": lastBuses}
		return None
	
	def updateCheckins(self, checkins):
		# purge checkins that are more than 30 minutes old
		self.database.checkins.remove({"time": {"$lt": datetime.utcnow() + timedelta(hours=-5, minutes=-30)}})
		if len(checkins) > 0:
			self.database.checkins.insert(checkins)
	

