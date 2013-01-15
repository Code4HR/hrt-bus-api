from datetime import datetime, timedelta
from pymongo import Connection

class HRTDatabase:
	def __init__(self, uri):
		self.client = Connection(uri)
		self.database = self.client.hrt
	
	# get bus route mappings that are not more than 30 minutes old
	def getBusRouteMappings(self):
		mappings = {} 
		for mapping in self.database['busRouteMappings'].find():
			if mapping['time'] > datetime.utcnow() + timedelta(hours=-5, minutes=-30):
				mappings[mapping['busId']] = mapping
		return mappings
	
	def setBusRouteMappings(self, mappings):
		self.database['busRouteMappings'].remove()
		if len(mappings) > 0:
			self.database['busRouteMappings'].insert(mappings)
	
	# return the last time to the minute that a bus checked in and a list of all buses that checked in during that minute 
	def getLastCheckinSummary(self):
		if self.database['checkins'].find().count() > 0:
			lastTime = self.database['checkins'].find().sort("$natural", -1)[0]["time"]
			lastBuses = self.database['checkins'].find({"time" : lastTime}).distinct("busId")
			return {"time": lastTime, "busIds": lastBuses}
		return None
	
	def updateCheckins(self, checkins):
		# purge checkins that are more than 30 minutes old
		self.database['checkins'].remove({"time": {"$lt": datetime.utcnow() + timedelta(minutes=-30)}})
		if len(checkins) > 0:
			self.database['checkins'].insert(checkins)
	
	def getTripId(self, checkin):
		collectionName = 'gtfs_' + checkin.time.strftime('%Y%m%d')
		checkinTime = (checkin.time + timedelta(hours=-5, minutes=checkin.adherence)).strftime('%H:%M:00')
		checkinTimePlus1 = (checkin.time + timedelta(hours=-5, minutes=checkin.adherence+1)).strftime('%H:%M:00')
		checkinTimeMinus1 = (checkin.time + timedelta(hours=-5, minutes=checkin.adherence-1)).strftime('%H:%M:00')
		scheduledStop = self.database[collectionName].find_one({
																"route_id" : checkin.routeId, 
																"stop_id": checkin.stopId, 
																"direction_id": checkin.direction,
																"$or" : [
																	{"arrival_time": checkinTime}, 
																	{"arrival_time": checkinTimePlus1}, 
																	{"arrival_time": checkinTimeMinus1}
																]
															})
		if scheduledStop is None:
			print "No scheduled stop found for the following checkin at {0}, {1}, or {2}".format(checkinTimeMinus1, checkinTime, checkinTimePlus1)
			print checkin.__dict__
			return None
		return scheduledStop['trip_id']
	

