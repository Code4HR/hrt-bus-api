hrt-bus-api
===========

Python scripts and Flask app that transform, store, and expose HRT Bus data through a RESTful API. API's don't make for good demos, so we've created an HRT Bus Finder App.

demo site: http://lit-inlet-3610.herokuapp.com

Problem
===========================
HRT exposes the real time location of there buses at `ftp://216.54.15.3/Anrd/hrtrtf.txt`. Unfortunately, this file gives us less than five minutes of data and most of the entries don't have a route number associated with them. Riders lookup bus information by route number, so without it, the data isn't very useful.

Solution
===========================
### Transform and Store

* [Process FTP](https://github.com/brigade-hrva/hrt-bus-api/tree/master/scripts/process-ftp) - Fetches the HRT FTP file and stores the data in MongoDB. Also attempts to set route number when it's missing.
* [Process GTFS](https://github.com/brigade-hrva/hrt-bus-api/tree/master/scripts/process-gtfs) - Fetches the HRT GTFS package and stores the schedulded stop times for a single day in MongoDB.

### Expose

Setup for Local Development (Mac or GNU/Linux)
===========================
* Step 1

Setup for Local Development (Windows)
===========================
* Step 1

Options for Deploying
===========================
### Scripts

* [Iron.io](http://www.iron.io/worker) - Each script has it's own README with instructions for deployment

### Flask Web Application

* [Heroku](http://www.heroku.com/) - Check this [wiki page](https://github.com/brigade-hrva/hrt-bus-api/wiki/Deploying-To-Heroku)

We're Here to Help
=====================
* Ben Schoenfeld - ben.schoenfeld@gmail.com - [@oilytheotter](http://twitter.com/oilytheotter)
* Search or post to our [Google Group](https://groups.google.com/a/codeforamerica.org/forum/#!forum/hrva-brigade) for the local "Brigade" 
