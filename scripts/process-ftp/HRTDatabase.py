import pytz
from datetime import datetime, timedelta
from pymongo import Connection

class HRTDatabase:
	def __init__(self, uri, db):
		self.client = Connection(uri)
		self.database = self.client[db]
	
	# get bus route mappings that are not more than 30 minutes old
	def getBusRouteMappings(self):
		mappings = {} 
		for mapping in self.database['busRouteMappings'].find():
			if mapping['time'] > datetime.utcnow() + timedelta(minutes=-30):
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
			return {"time": lastTime.replace(tzinfo=pytz.UTC), "busIds": lastBuses}
		return None
	
	def updateCheckins(self, checkins):
		# purge checkins that are more than 2 hours
		self.database['checkins'].remove({"time": {"$lt": datetime.utcnow() + timedelta(hours=-2)}})
		if len(checkins) > 0:
			self.database['checkins'].insert(checkins)
	
	def getScheduledStop(self, checkin):
		checkinLocalTime = checkin.time + timedelta(hours=-5)
		collectionName = 'gtfs_' + checkinLocalTime.strftime('%Y%m%d')
		scheduledStop = self.database[collectionName].find_one({ 
										"route_id" : checkin.routeId,
										"stop_id": checkin.stopId,
										"direction_id": checkin.direction,
										"arrival_time": { "$gte": checkin.time + timedelta(minutes=checkin.adherence - 2),
														  "$lte": checkin.time + timedelta(minutes=checkin.adherence + 2) }})
		if scheduledStop is None:
			print "No scheduled stop found for the following checkin in {0}".format(collectionName)
			print checkin.__dict__
			return None
			
		# get the stop sequence that OneBusAway uses
		scheduledStop['stop_sequence_OBA'] = self.database[collectionName].find({
													"trip_id": scheduledStop["trip_id"],
													"stop_sequence": {"$lt": scheduledStop["stop_sequence"]}}).count()
		
		return scheduledStop
	

