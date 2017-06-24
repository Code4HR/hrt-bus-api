import unittest
from web.app import getActiveRoutes, getBusesOnRoute, getBusesByRoute, getBusHistory

class TestBusHandler(unittest.TestCase):
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

    # class BusHandler:

    </api/routes/active>
    @getActiveRoutes : [routes].json
    # def active:
        - app
        - db
        - collectionPrefix
        (support_jsonp)
    </api/buses/on_route/:routeId>
    @getBusesOnRoute : route.id -> [checkin].json
    # def on_route:
        - app
        - dthandler
        - db
        (support_jsonp)
    </api/buses/routes>
    </api/buses/routes/:routeIds>
    @getBusesByRoute : [route.id]? -> [checkin].json
    # def in_routes(routes):
        - app
        - dthandler
        - db
        (support_jsonp)
    </api/buses/history/:busId>
    @getBusHistory : bus.id -> [checkin].json
        - app
        - dthandler
        - db
        (support_jsonp)
    """
