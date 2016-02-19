import unittest
from web.app import beforeRequest, index, busfinder, getApiInfo

class TestGeneralHandler(unittest.TestCase):
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

    # class GeneralHandler:
    - curDateTime : datetime

    !!@beforeRequest : ()
        - app
        - db
        - curDateTime
    </>
    @index : =>/busfinder
        - app
    </busfinder>
    </busfinder/:view>
    @busfinder : view? -> /busfinder.html
        - app
    </api>
    @getApiInfo : api
        - app
        - dthandler
        - db
        - curDateTime
        - collectionPrefix
        (support_jsonp)
    """

