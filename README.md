hrt-bus-api
===========

C# ASP.NET application that processes and exposes HRT Bus Data through an API

### Examples

- <http://hrtbusapi.apphb.com/example/ui>
- <http://hrtbusapi.apphb.com/refresh>

## Problem

HRT exposes the real time location of there buses at `ftp://216.54.15.3/Anrd/hrtrtf.txt`. Unfortunately, this file gives us less than five minutes of data and most of the entries don't have a route number associated with them. Riders lookup bus information by route number, so without it, the data isn't very useful.

## Solution

This application periodically pulls[*](#Polling_Hack) the HRT data and caches it for an hour. Each data set from HRT typically contains 10% of the necessary route information. The application's cache is able to build route information to more than 80%. The application exposes the cached data through a RESTful API.

## Hosting

The application is currently hosted by [Ben's](https://github.com/bschoenfeld) AppHarbor account at <http://hrtbusapi.apphb.com>. Any push to this repository (including those that don't touch code) will trigger AppHarbor to rebuild and deploy the app, which will clear the cache. The app needs 5-10 minutes to rebuild the cache to the point where it has enough route information to be useful.

## API

### /API/routes

Returns an array of all known routes
```javascript
[1,2,3]
```

### /API/route/{routeNumber}

Returns an object with the route number and an array of the most recent checkin for each bus on the route. Route Number 0 returns all buses without a route.
```javascript
{
  buses: [
    {
      id: 1219,
      route: 2,
      direction: 1,
      datetime: "/Date(1351502600000)/",
      lat: 37.0128547,
      lon: -76.3649448,
      adherence: 0
    }
  ],
  route: 2
}
```

### /API/buses

Returns an array of all known buses
```javascript
[1001,2002,3003]
```

Add the route parameter and specify true or false to get only buses with or without a route
```html
buses?route=true
buses?route=false
```

### /API/bus/{busId}

Returns an array of all the checkins the bus has made in the last hour

```javascript
[
  {
    id: 1219,
    route: 2,
    direction: 1,
    datetime: "/Date(1351502600000)/",
    lat: 37.0128547,
    lon: -76.3649448,
    adherence: 0
  },
  {
    id: 1219,
    route: 2,
    direction: 1,
    datetime: "/Date(1351502540000)/",
    lat: 37.0128547,
    lon: -76.3649448,
    adherence: 0
  }
]
```

## * Polling Hack

Data needs to be fetched from the HRT FTP site once a minute or more. ASP.NET doesn't really like background processes and AppHarbor stops being free when you add a background worker. To get around these issues, the application exposes a trigger at `/refresh`. The trigger causes the app to pull the HRT data from their FTP site and load it into the application. If you browse to the trigger, it will tell you the result of the refresh.

There is a second application running on AppHarbor that pulls this trigger. It's a simple console app that uses a while loop and thread sleep to make one web request to that link every 20 seconds.