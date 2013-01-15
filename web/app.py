from flask import Flask
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
	buses = db['checkins'].find({"routeId":routeId}).distinct('busId')
	buses.sort()
	return str(buses)
	
@app.route('/api/bus/<int:busId>/')
def getBusHistory(busId):
	return str(list(db['checkins'].find({"busId":busId}).sort('time', pymongo.DESCENDING)))

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
