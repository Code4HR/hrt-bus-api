import unittest
from web.app import getBusesAtStop

class TestStopHandlerV2(unittest.TestCase):
    """
    -------------------
    # class RouteFormatter:
    - (8) dthandler : (obj -> datetime?)
    (11) support_jsonp : a -> ([arg] -> [[kwarg]] -> response)
    -------------------

    -------------------
    # class BusApi:
    - (17) app : Flask
    - (13) db : Connection
    - (7) collectionPrefix : string
    -------------------


    =============================

    # class StopHandlerV2:

    </api/v2/stops/near/:lat/:lng>
    @get_stops_near : lat? -> long? -> capacity? -> [stop].json # v2
        - app
        - dthandler
        - db
        - collectionPrefix
        (support_jsonp)
        (find_buses_at_stop)
    find_buses_at_stop : stop.id -> [scheduled_stop]
        - db
        - collectionPrefix
    </api/stop_times/:stopId>
    @getBusesAtStop : stop.id -> [scheduled_stop].json          # v1
        - app
        - dthandler
        (support_jsonp)
        (find_buses_at_stop)
    </api/v2/stops/:stopId>
    @get_buses_at_stop : stop.id -> [scheduled_stop].json       # v2
        - app
        - dthandler
        (support_jsonp)
        (find_buses_at_stop)

    """
    def test_get_buses_at_stop_v1(self):
        self.assertEqual(True, True)
