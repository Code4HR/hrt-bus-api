import unittest
from web.app import getStopsNearIntersection, getStopsNear, getNextBus

class TestStopHandler(unittest.TestCase):
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

    # class StopHandler:

    </api/stops/near/intersection/:city/:intersection>
    @getStopsNearIntersection : city -> intersection -> [stop].json
        - app
        (getStopsNear)
    </api/stops/near/:lat/:lng>
    @getStopsNear : lat -> lng -> [stop].json   # v1
        - app
        - db
        - collectionPrefix
        (support_jsonp)
    </api/stops/id/:stopIds>
    @getStopsById : ids_string -> [stop].json
        - app
        - db
        - collectionPrefix
        (support_jsonp)
    </api/stop_times/:routeId/:stopId>
    @getNextBus : route.id -> stop.id -> [stop].json
        - app
        - dthandler
        - db
        - collectionPrefix
        (support_jsonp)
    """

