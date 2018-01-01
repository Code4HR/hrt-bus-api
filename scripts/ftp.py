import os
from ftplib import FTP
from datetime import datetime, timedelta
from bus import Checkin
from database import HRTDatabase

DATABASE = HRTDatabase(os.environ["db_uri"], os.environ["db_name"])
PROCESSOR = None
LAST_REPEAT = None

def process(event, context):
    global PROCESSOR
    PROCESSOR = Processor()
    print "Read {0} Bus Route Mappings".format(len(PROCESSOR.bus_route_mappings))

    ftp = FTP('52.170.192.86')
    ftp.login()
    print ftp.sendcmd('PASV')
    ftp.cwd('Anrd')
    ftp.retrlines('RETR hrtrtf.txt', processData)

    if PROCESSOR.last_checkins is not None:
        print "Latest Checkin Time From Previous Run: {0}".format(PROCESSOR.last_checkins["time"])
    print "Latest Previously Processed Checkin Time From This Run: {0}".format(PROCESSOR.last_repeat)

    DATABASE.setBusRouteMappings(PROCESSOR.bus_route_mappings.values())
    print "Inserted {0} Bus Route Mappings".format(len(PROCESSOR.bus_route_mappings))

    DATABASE.updateCheckins(PROCESSOR.checkin_docs)
    print "Added {0} Checkins".format(len(PROCESSOR.checkin_docs))

    DATABASE.updateRealTimeArrivals(PROCESSOR.schedule_changes)

    for key, value in PROCESSOR.stats.iteritems():
        print "{0} {1}".format(key, value)

class Processor:
    def __init__(self):
        self.bus_route_mappings = DATABASE.getBusRouteMappings()
        self.last_checkins = DATABASE.getLastCheckinSummary()
        self.checkin_docs = []
        self.schedule_changes = {}
        self.last_repeat = None
        self.stats = {
            'lines': 0,
            'invalid': 0,
            'processed': 0,
            'hadRoute': 0,
            'foundRoute': 0,
            'foundTrip': 0,
            'arriveTimesUpdated': 0
        }

def processData(text):
    if not text.strip():
        return

    PROCESSOR.stats['lines'] += 1

    try:
        checkin = Checkin(text)
    except ValueError:
        PROCESSOR.stats['invalid'] += 1
        return

    if checkinProcessed(checkin):
        PROCESSOR.last_repeat = checkin.time
        return

    PROCESSOR.stats['processed'] += 1

    if hasattr(checkin, 'routeId'):
        checkin.tripId = None
        checkin.blockId = None
        checkin.lastStopSequence = None
        checkin.lastStopSequenceOBA = None
        if hasattr(checkin, 'adherence'):
            scheduled_stop = DATABASE.getScheduledStop(checkin)
            if scheduled_stop is not None:
                PROCESSOR.stats['foundTrip'] += 1
                checkin.tripId = scheduled_stop['trip_id']
                checkin.blockId = scheduled_stop['block_id']
                checkin.lastStopSequence = scheduled_stop['stop_sequence']
                checkin.lastStopSequenceOBA = scheduled_stop['stop_sequence_OBA']
                checkin.scheduleMatch = True
        if checkin.tripId is None and checkin.busId in PROCESSOR.bus_route_mappings:
            checkin.tripId = PROCESSOR.bus_route_mappings[checkin.busId]['tripId']
            checkin.blockId = PROCESSOR.bus_route_mappings[checkin.busId]['blockId']
            checkin.lastStopSequence = PROCESSOR.bus_route_mappings[checkin.busId]['lastStopSequence']
            checkin.lastStopSequenceOBA = PROCESSOR.bus_route_mappings[checkin.busId]['lastStopSequenceOBA']
        PROCESSOR.bus_route_mappings[checkin.busId] = {
            'busId': checkin.busId,
            'routeId' : checkin.routeId,
            'direction': checkin.direction,
            'tripId': checkin.tripId,
            'blockId': checkin.blockId,
            'lastStopSequence': checkin.lastStopSequence,
            'lastStopSequenceOBA': checkin.lastStopSequenceOBA,
            'time': checkin.time
        }
        PROCESSOR.stats['hadRoute'] += 1
    elif checkin.busId in PROCESSOR.bus_route_mappings:
        checkin.routeId = PROCESSOR.bus_route_mappings[checkin.busId]['routeId']
        checkin.direction = PROCESSOR.bus_route_mappings[checkin.busId]['direction']
        checkin.tripId = PROCESSOR.bus_route_mappings[checkin.busId]['tripId']
        checkin.blockId = PROCESSOR.bus_route_mappings[checkin.busId]['blockId']
        checkin.lastStopSequence = PROCESSOR.bus_route_mappings[checkin.busId]['lastStopSequence']
        checkin.lastStopSequenceOBA = PROCESSOR.bus_route_mappings[checkin.busId]['lastStopSequenceOBA']
        PROCESSOR.stats['foundRoute'] += 1

    if hasattr(checkin, 'adherence') and hasattr(checkin, 'blockId'):
        collection, updates = DATABASE.getRealTimeArrivalUpdates(checkin)
        if collection not in PROCESSOR.schedule_changes:
            PROCESSOR.schedule_changes[collection] = []
        PROCESSOR.schedule_changes[collection].extend(updates)
        PROCESSOR.stats['arriveTimesUpdated'] += len(updates)

    PROCESSOR.checkin_docs.append(checkin.__dict__)

def checkinProcessed(checkin):
    if PROCESSOR.last_checkins is None:
        return False
    if checkin.time == PROCESSOR.last_checkins["time"]:
        return checkin.busId in PROCESSOR.last_checkins["busIds"]
    return checkin.time < PROCESSOR.last_checkins["time"]
