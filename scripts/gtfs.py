import json
import os
import pytz
import sys
from StringIO import StringIO
from urllib import urlopen
from zipfile import ZipFile
from csv import DictReader
from datetime import datetime, time, timedelta
from database import HRTDatabase

EST = pytz.timezone('US/Eastern')

def process(event, context):
    print event

    now = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(EST)
    print 'Running at ' + str(now)

    database = HRTDatabase(os.environ["db_uri"], os.environ["db_name"])
    if 'daysFromNow' not in event:
        database.removeOldGTFS(now)

    file_url = 'http://googletf.gohrt.com/google_transit.zip'
    zip_file = ZipFile(StringIO(urlopen(file_url).read()))

    days_from_now = 1
    if 'daysFromNow' in event:
        days_from_now = event['daysFromNow']
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    cur_date = (now + timedelta(days=days_from_now)).date()
    midnight = datetime.combine(cur_date, time.min)
    cur_week_day = days[cur_date.weekday()]
    print cur_week_day + " " + str(cur_date)

    active_service_ids = []
    calendar = DictReader(open_from_zipfile(zip_file, "calendar.txt"))
    for row in calendar:
        start = datetime.strptime(row['start_date'], "%Y%m%d").date()
        end = datetime.strptime(row['end_date'], "%Y%m%d").date()
        if cur_date >= start and cur_date <= end and row[cur_week_day] == '1':
            active_service_ids.append(row['service_id'])
    print active_service_ids

    active_trips = {}
    trips = DictReader(open_from_zipfile(zip_file, "trips.txt"))
    for row in trips:
        if row['service_id'] in active_service_ids:
            active_trips[row['trip_id']] = row
    print str(len(active_trips)) + " active trips"

    active_stop_times = []
    stop_times = DictReader(open_from_zipfile(zip_file, "stop_times.txt"))
    for row in stop_times:
        if row['trip_id'] in active_trips:
            try:
                trip = active_trips[row['trip_id']]
                row['route_id'] = int(trip['route_id'])
                row['direction_id'] = int(trip['direction_id'])
                row['block_id'] = trip['block_id']
                row['stop_id'] = row['stop_id']
                row['stop_sequence'] = int(row['stop_sequence'])

                arrive_time = row['arrival_time'].split(':')
                naive_arrive_time = midnight + timedelta(
                    hours=int(arrive_time[0]), minutes=int(arrive_time[1])
                )
                local_arrive_time = EST.localize(naive_arrive_time, is_dst=False)
                row['arrival_time'] = local_arrive_time.astimezone(pytz.utc)

                depart_time = row['departure_time'].split(':')
                naive_dept_time = midnight + timedelta(
                    hours=int(depart_time[0]), minutes=int(depart_time[1])
                )
                local_dept_time = EST.localize(naive_dept_time, is_dst=False)
                row['departure_time'] = local_dept_time.astimezone(pytz.utc)

                active_stop_times.append(row)
            except ValueError:
                pass
    print str(len(active_stop_times)) + " active stop times"

    database.insertGTFS(active_stop_times, cur_date)

    stops = []
    stops_reader = DictReader(open_from_zipfile(zip_file, "stops.txt"))
    for row in stops_reader:
        try:
            stops.append({
                'stopId': row['stop_id'],
                'stopName': row['stop_name'],
                'location': [float(row['stop_lat']), float(row['stop_lon'])]
            })
        except ValueError:
            pass
    print str(len(stops)) + " stops"
    database.insertStops(stops, cur_date)

    routes = []
    routes_reader = DictReader(open_from_zipfile(zip_file, "routes.txt"))
    for row in routes_reader:
        try:
            row['route_id'] = int(row['route_id'])
            routes.append(row)
        except ValueError:
            pass
    print str(len(routes)) + " routes"
    database.insertRoutes(routes, cur_date)

    print "Generating Destinations Collection"
    destinations = []
    for trip in database.getFinalStops(cur_date):
        destinations.append({
            'tripId': trip['_id'],
            'stopName': database.getStopName(trip['stopId'], cur_date)
        })
    print str(len(destinations)) + " destinations"
    database.insertDestinations(destinations, cur_date)

    print "Generating Indexes"
    database.generateIndicesForGTFS(cur_date)

def open_from_zipfile(zip_file, filename):
    # Remove UTF-8 BOM (http://stackoverflow.com/a/18664752/438281)
    return StringIO(
        zip_file
        .open(filename)
        .read()
        .decode("utf-8-sig")
        .encode("utf-8")
    )
