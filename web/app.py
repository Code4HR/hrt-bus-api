from datetime import datetime, timedelta
from flask import Flask
from geopy import geocoders
import os
import pymongo

app = Flask(__name__)
db = pymongo.Connection(os.environ['MONGO_URI']).hrt

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/api/routes/')
def getActiveRoutes():
	routes = db['checkins'].distinct('routeId')
	routes.sort()
	return str(routes)

@app.route('/api/route/<int:routeId>/')
def getBusesOnRoute(routeId):
	checkins = {}
	for checkin in db['checkins'].find({"routeId":routeId}).sort('time'):
		checkins[checkin['busId']] = checkin
	return str(checkins)
	
@app.route('/api/bus/<int:busId>/')
def getBusHistory(busId):
	return str(list(db['checkins'].find({"busId":busId}).sort('time', pymongo.DESCENDING)))

@app.route('/api/stop/<city>/<intersection>/')
def getNearestStop(city, intersection):
	geocoders.Google()
	place, (lat, lng) = geocoders.Google().geocode("{0}, {1}, VA".format(intersection, city))
	return str(db['stops'].find_one({"location": {"$near": [lng, lat]}}))

@app.route('/api/nextbus/<int:routeId>/<int:stopId>/')
def getNextBus(routeId, stopId):
	time = datetime.utcnow()
	collectionName = 'gtfs_' + (time + timedelta(hours=-5)).strftime('%Y%m%d')
	scheduledStops = list(db[collectionName].find({"route_id":routeId, "stop_id":stopId}).sort('arrival_time'))
	for stop in scheduledStops:
		busOnTrip = db['checkins'].find_one({"tripId":stop["trip_id"]})
		if busOnTrip is not None:
			stop['adherence'] = busOnTrip['adherence']
	return str(scheduledStops)

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
