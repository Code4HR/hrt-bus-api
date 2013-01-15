import os
from flask import Flask
from pymongo import Connection

app = Flask(__name__)
db = Connection(os.environ['MONGO_URI']).hrt

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/api/routes/')
def getActiveRoutes():
	routes = db['checkins'].distinct('routeId')
	routes.sort()
	return str(routes)


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
