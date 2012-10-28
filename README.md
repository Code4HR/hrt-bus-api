hrt-bus-api
===========

C# ASP.NET application that processes and exposes HRT Bus Data through an API

## Problem

HRT exposes the real time location of there buses [here](ftp://216.54.15.3/Anrd/hrtrtf.txt). Unfortunately, this file gives us less than five minutes of data and most of the entries don't have a route number associated with them. Riders lookup bus information by route number, so without it, the data isn't very useful.

## Solution

This application periodically pulls the HRT data* and caches it for an hour. Each data set from HRT typically contains 20% of the necessary route information. The application's cache is able to build route information to more than 80%. The application exposes the cached data through a RESTful API.