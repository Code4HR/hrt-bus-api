hrt-bus-api
===========

C# ASP.NET application that processes and exposes HRT Bus Data through an API

## Problem

HRT exposes the real time location of there buses [here](ftp://216.54.15.3/Anrd/hrtrtf.txt). Unfortunately, this file gives us less than five minutes of data and most of the entries don't have a route number associated with them. Riders lookup bus information by route number, so without it, the data isn't very useful.

## Solution

This application periodically pulls[*](#Polling_Hack) the HRT data and caches it for an hour. Each data set from HRT typically contains 20% of the necessary route information. The application's cache is able to build route information to more than 80%. The application exposes the cached data through a RESTful API.

## Hosting

The application is currently hosted by [Ben's](https://github.com/bschoenfeld) AppHarbor account at [http://hrtbusapi.apphb.com](http://hrtbusapi.apphb.com).

## API

- `/API/route`
- `/API/route/{routeNumber}`
- `/API/bus/{busId}`

## * Polling Hack

Data needs to be fetched from the HRT FTP site once a minute or more. ASP.NET doesn't really like background processes and AppHarbor stops being free when you add a background worker. To get around these issues, the application exposes a trigger at `/refresh`. The trigger causes the app to pull the HRT data from their FTP site and load it into the application. If you browse to the trigger, it will tell you the result of the refresh.

There is a second application running on AppHarbor that pulls this trigger. It's a simple console app that uses a while loop and thread sleep to make one web request to that link every 20 seconds.