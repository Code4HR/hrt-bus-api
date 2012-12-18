hrt-bus-api
===========

C# ASP.NET application that processes and exposes HRT Bus Data through an API

### Examples

- <http://hrtbusapi.azurewebsites.net/example/ui>
- <http://hrtbusapi.azurewebsites.net/refresh>

## Problem

HRT exposes the real time location of there buses at `ftp://216.54.15.3/Anrd/hrtrtf.txt`. Unfortunately, this file gives us less than five minutes of data and most of the entries don't have a route number associated with them. Riders lookup bus information by route number, so without it, the data isn't very useful.

## Solution

This application periodically pulls the HRT data and caches it for an hour. Each data set from HRT typically contains 10% of the necessary route information. The application's cache is able to build route information to more than 80%. The application exposes the cached data through a RESTful API.

## Hosting

The application is currently hosted by [Ben's](https://github.com/bschoenfeld) Azure account at <http://hrtbusapi.azurewebsites.net>.

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

## HRT Data Refresh

### /refresh

The application requests this URL once every 20 seconds to refresh the real time bus data from HRT. This URL can be requested from any browser to run a sort of health check on the application. The following data will be returned. If the application is running normally, there should be almost 300 checkins in the FTP file and no more than 100 should be new. There should be around 10,000 checkins in memory and about 90% should have routes. The last auto-refresh (in EST) should be less than 1 minute old.

```
293 checkins in FTP file.
0 were new.
0 new checkins didn't have a route. Routes were found for 0 of those.
0 were removed because they were more than an hour old.
801 checkins now in memory.
34% have a route.
12 auto refreshes.
Last auto-refresh at 12/1/2012 4:30:14 PM
```
