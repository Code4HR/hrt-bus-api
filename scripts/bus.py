import pytz
from datetime import datetime, timedelta

class Checkin:
    def __init__(self, data):
        parts = data.split(',')

        # checkin time
        local_tz = pytz.timezone('US/Eastern')

        utc = datetime.utcnow()
        utc = utc.replace(tzinfo=pytz.utc)
        local = utc.astimezone(local_tz)

        # handle checkins from both 12/31/N and 1/1/N+1
        year = local.year
        if parts[1].startswith('12/') and local.month == 1:
            year -= 1
        elif parts[1].startswith('1/') and local.month == 12:
            year += 1

        #print local, data, year

        naive = datetime.strptime('{} {}/{}'.format(
            parts[0], parts[1], str(year)
        ), '%H:%M:%S %m/%d/%Y')
        local_dt = local_tz.localize(naive, is_dst=False)
        self.time = local_dt.astimezone(pytz.utc)

        # bus id
        self.busId = int(parts[2])

        # location
        if parts[4] == 'V':
            location = parts[3].split('/')
            lat = float(location[0][:2] + '.' + location[0][2:])
            lon = float(location[1][:3] + '.' + location[1][3:])
            self.location = [lat, lon]

        # adherence
        if parts[6] == 'V':
            self.adherence = int(parts[5])

        if len(parts) == 10:
            self.routeId = int(parts[7])
            self.direction = int(parts[8]) - 1
            self.stopId = parts[9].zfill(4)
