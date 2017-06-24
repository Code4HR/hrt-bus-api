import unittest
from web.app import tripUpdate, vehiclePosition

class TestGtfsHandler(unittest.TestCase):
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

    # class GtfsHandler:

    </gtfs/trip_update>
    @tripUpdate : feed (?)
        - app
        - db
    </gtfs/vehiclePosition>
    @vehiclePosition : feed (?)
        - app
        - db
    """

