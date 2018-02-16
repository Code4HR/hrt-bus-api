import os
import pytz
from datetime import datetime, timedelta
from pymongo import MongoClient, GEO2D, ASCENDING, UpdateOne

class HRTDatabase:
    def __init__(self):
        self.database = MongoClient(os.environ['MONGODB_URI']).hrt

    def removeOldGTFS(self, date):
        print "Removing Old GTFS Data"
        collection_prefix = self.genCollectionName('', date)
        for collection in self.database.collection_names():
            if collection.find('_') != -1 and (not collection.endswith(collection_prefix)):
                self.database.drop_collection(collection)

    def insertGTFS(self, data, date):
        self.insertData(self.genCollectionName('gtfs_', date), data)

    def insertStops(self, data, date):
        collection_name = self.genCollectionName('stops_', date)
        self.insertData(collection_name, data)
        self.database[collection_name].ensure_index([('location', GEO2D)])

    def insertRoutes(self, data, date):
        self.insertData(self.genCollectionName('routes_', date), data)

    def insertDestinations(self, data, date):
        self.insertData(self.genCollectionName('destinations_', date), data)

    def getStopName(self, stop_id, date):
        collection_name = self.genCollectionName('stops_', date)
        stop = self.database[collection_name].find_one({"stopId": stop_id})
        return stop['stopName']

    def getFinalStops(self, date):
        collection_name = self.genCollectionName('gtfs_', date)
        final_stops = self.database[collection_name].aggregate([
            {"$group": {
                "_id": "$trip_id",
                "stopId": {"$last": "$stop_id"},
                "sequence": {"$last": "$stop_sequence"}
            }}
        ])
        return final_stops

    def generateIndicesForGTFS(self, date):
        collection_name = self.genCollectionName('gtfs_', date)
        self.database[collection_name].create_index([
            ("block_id", ASCENDING)
        ], background=True)
        self.database[collection_name].create_index([
            ("block_id", ASCENDING),
            ("arrival_time", ASCENDING)
        ], background=True)
        self.database[collection_name].create_index([
            ("block_id", ASCENDING),
            ("actual_arrival_time", ASCENDING)
        ], background=True)
        self.database[collection_name].create_index([
            ("stop_id", ASCENDING),
            ("arrival_time", ASCENDING),
            ("actual_arrival_time", ASCENDING)
        ], background=True)
        self.database[collection_name].create_index([
            ("route_id", ASCENDING),
            ("stop_id", ASCENDING),
            ("direction_id", ASCENDING),
            ("arrival_time", ASCENDING)
        ], background=True)
        self.database[collection_name].create_index([
            ("route_id", ASCENDING),
            ("stop_id", ASCENDING),
            ("direction_id", ASCENDING),
            ("departure_time", ASCENDING)
        ], background=True)

    def genCollectionName(self, prefix, date):
        return prefix + date.strftime('%Y%m%d')

    def insertData(self, collection_name, data):
        if len(data) > 0:
            self.database[collection_name].remove()
            self.database[collection_name].insert_many(data)


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

    # return the last time to the minute that a bus checked in and
    # a list of all buses that checked in during that minute
    def getLastCheckinSummary(self):
        if self.database['checkins'].find().count() > 0:
            last_time = self.database['checkins'].find().sort("$natural", -1)[0]["time"]
            last_buses = self.database['checkins'].find({"time" : last_time}).distinct("busId")
            return {"time": last_time.replace(tzinfo=pytz.UTC), "busIds": last_buses}
        return None

    def updateCheckins(self, checkins):
        # purge checkins that are more than 2 hours
        self.database['checkins'].remove({"time": {"$lt": datetime.utcnow() + timedelta(hours=-2)}})
        if len(checkins) > 0:
            self.database['checkins'].insert(checkins)

    def getRealTimeArrivalUpdates(self, checkin):
        checkin_local_time = checkin.time + timedelta(hours=-5)
        collection_name = 'gtfs_' + checkin_local_time.strftime('%Y%m%d')
        stop_times = self.database[collection_name].find({
            'block_id': checkin.blockId,
            '$or': [
                {'arrival_time': {
                    '$gte': datetime.utcnow() + timedelta(minutes=-5-checkin.adherence),
                    '$lte': datetime.utcnow() + timedelta(minutes=30-checkin.adherence)
                }},
                {'actual_arrival_time': {
                    '$gte': datetime.utcnow() + timedelta(minutes=-5),
                    '$lte': datetime.utcnow() + timedelta(minutes=30)
                }}
            ]
        }, {'arrival_time': 1, 'actual_arrival_time': 1})
        updates = []
        for stoptime in stop_times:
            new_arrival_time = stoptime['arrival_time'] - timedelta(minutes=checkin.adherence)
            if 'actual_arrival_time' not in stoptime or new_arrival_time != stoptime['actual_arrival_time']:
                updates.append(UpdateOne(
                    {'_id': stoptime['_id']},
                    {'$set': {'actual_arrival_time': new_arrival_time}}
                ))
        return (collection_name, updates)

    def updateRealTimeArrivals(self, updates):
        for collection_name in updates:
            if updates[collection_name]:
                result = self.database[collection_name].bulk_write(updates[collection_name])
                #print result.bulk_api_result

    def getScheduledStop(self, checkin):
        checkin_local_time = checkin.time + timedelta(hours=-5)
        collection_name = 'gtfs_' + checkin_local_time.strftime('%Y%m%d')
        scheduled_stop = self.database[collection_name].find_one({
            "route_id" : checkin.routeId,
            "stop_id": checkin.stopId,
            "direction_id": {"$ne": checkin.direction},
            "$or": [
                {"arrival_time": {
                    "$gte": checkin.time + timedelta(minutes=checkin.adherence - 2),
                    "$lte": checkin.time + timedelta(minutes=checkin.adherence + 2)
                }},
                {"departure_time": {
                    "$gte": checkin.time + timedelta(minutes=checkin.adherence - 2),
                    "$lte": checkin.time + timedelta(minutes=checkin.adherence + 2)
                }}
            ]
        })
        if scheduled_stop is None:
            print "No scheduled stop found for the following checkin in {0}".format(collection_name)
            print checkin.__dict__
            return None

        # get the stop sequence that OneBusAway uses
        scheduled_stop['stop_sequence_OBA'] = self.database[collection_name].find({
            "trip_id": scheduled_stop["trip_id"],
            "stop_sequence": {"$lt": scheduled_stop["stop_sequence"]}
        }).count()

        return scheduled_stop
