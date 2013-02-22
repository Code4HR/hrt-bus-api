# hrt-bus-api
Python scripts and Flask app that transform, store, and expose HRT Bus data through a RESTful API. API's don't make for good demos, so we've created an HRT Bus Finder App.

demo site: http://lit-inlet-3610.herokuapp.com

## Problem
HRT exposes the real time location of there buses at `ftp://216.54.15.3/Anrd/hrtrtf.txt`. Unfortunately, this file gives us less than five minutes of data and most of the entries don't have a route number associated with them. Riders lookup bus information by route number, so without it, the data isn't very useful.

## Solution

### Transform and Store Data - Python Scripts
* [Process FTP](https://github.com/brigade-hrva/hrt-bus-api/tree/master/scripts/process-ftp) - Fetches the HRT FTP file and stores the data in MongoDB. Also attempts to set route number when it's missing.
* [Process GTFS](https://github.com/brigade-hrva/hrt-bus-api/tree/master/scripts/process-gtfs) - Fetches the HRT GTFS package and stores the schedulded stop times for a single day in MongoDB.

### Expose Data - Python Flask
* Web App
    * [RESTful API](https://github.com/brigade-hrva/hrt-bus-api/wiki/RESTful-API)
    * Bus Finder

## Setup for Local Development
If you would like to develop the scripts, you will need your own MongoDB instance. I recommend [MongoLab](https://mongolab.com/welcome/). If you just want to work on the web app, feel free to skip the part about the scripts. Read-only access is provided to a MongoDB instance that is being populated with real-time bus data.

### Scripts

### Web App
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
    
6. Install dependencies

    ```
    $ pip install -r requirements.txt
    ```
    
7. Set MongoDB URI (substitue your own MongoDB instance if you have one)

    ```
    $ export MONGO_URI=mongodb://hrt_web_app:cfa@ds045897.mongolab.com:45897/hrt
    ```
    
8. Change to the web directory and run the flask app

    ```
    $ cd web
    $ python app.py 
    ```
    
9. Browse to `http://0.0.0.0:5000/`

## Deployment

### Scripts
* [Iron.io](http://www.iron.io/worker) - Each script has it's own README with instructions for deployment

### Flask Web Application
* [Heroku](http://www.heroku.com/) - Check this [wiki page](https://github.com/brigade-hrva/hrt-bus-api/wiki/Deploying-To-Heroku)

## We're Here to Help
* Ben Schoenfeld - ben.schoenfeld@gmail.com - [@oilytheotter](http://twitter.com/oilytheotter)
* Search or post to our [Google Group](https://groups.google.com/a/codeforamerica.org/forum/#!forum/hrva-brigade) for the local "Brigade" 
