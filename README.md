# hrt-bus-api
HRT Bus API publishes real time bus data from Hampton Roads Transit through an application programming interface for developers to make apps from it.

HRT Bus API consists of Python scripts and a Flask app that transform, store, and expose HRT Bus data through a RESTful API. API's don't make for good demos, so we've created an HRT Bus Finder App.

## Try It
* Web App: [hrtb.us](http://hrtb.us)
* REST Api: [api.hrtb.us/api](http://api.hrtb.us/api/)

## Problem
HRT exposes the real time location of their buses at `ftp://216.54.15.3/Anrd/hrtrtf.txt`. Unfortunately, this file gives us less than five minutes of data and most of the entries don't have a route number associated with them. Riders lookup bus information by route number, so without it, the data isn't very useful.

## Solution

### Transform and Store Data - Python Scripts
* [Process GTFS](https://github.com/c4hrva/hrt-bus-api/tree/master/scripts/gtfs.py) - Fetches the HRT GTFS package and stores the scheduled stop times for a single day in MongoDB.
* [Process FTP](https://github.com/c4hrva/hrt-bus-api/tree/master/scripts/ftp.py) - Fetches the HRT FTP file and stores the data in MongoDB. Also attempts to set route number when it's missing.

### Expose Data - Python Flask
* Web App
    * [RESTful API](https://github.com/c4hrva/hrt-bus-api/wiki/RESTful-API)
    * Bus Finder
    
      ![Bus Finder](https://raw.github.com/bschoenfeld/hrt-bus-api/master/screenshot.png "Bus Finder")

## Setup for Local Development

1. Install [Python 2](http://wiki.python.org/moin/BeginnersGuide/Download)
2. Install [virtualenv](https://pypi.python.org/pypi/virtualenv)
3. Clone this repo
4. Create a virtual environment in the top level directory of the repo

    ```
    $ virtualenv venv --distribute
    ```
    
5. Activate the environment

    ```
    $ source venv/bin/activate
    ```
    -OR-  for Windows
    ```
    $ venv\Scripts\activate.bat
    ```    
    
6. Install dependencies

    ```
    $ pip install -r requirements.txt
    ```

### Scripts
If you would like to develop the scripts, you will need your own MongoDB instance. I recommend [MongoLab](https://mongolab.com/welcome/). If you just want to work on the web app, feel free to skip the part about the scripts. Read-only access is provided to a MongoDB instance that is being populated with real-time bus data.

### Web App

1. Set MongoDB URI (substitue your own MongoDB instance if you have one)

    ```
    $ export MONGO_URI=mongodb://hrt_web_app:cfa@ds045897.mongolab.com:45897/hrt
    ```
    -OR-  for Windows
    ```
    $ set MONGO_URI=mongodb://hrt_web_app:cfa@ds045897.mongolab.com:45897/hrt
    ```
2. Change to the web directory and run the flask app

    ```
    $ cd web
    $ python app.py 
    ```
    
3. Browse to `http://0.0.0.0:5000/`

## Deployment

### Scripts
* AWS Lambda - Check this [README](https://github.com/c4hrva/hrt-bus-api/tree/master/scripts/README.md)

### Flask Web Application
* [Heroku](http://www.heroku.com/) - Check this [wiki page](https://github.com/c4hrva/hrt-bus-api/wiki/Deploying-To-Heroku)

## We're Here to Help
* Ben Schoenfeld - ben.schoenfeld@gmail.com - [@oilytheotter](http://twitter.com/oilytheotter)
* Search or post to our [Google Group](https://groups.google.com/a/codeforamerica.org/forum/#!forum/hrva-brigade) for the local "Brigade" 
