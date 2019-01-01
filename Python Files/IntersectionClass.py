import sys
import psycopg2
import sets
from math import sin, cos, sqrt, atan2, radians


class IntersectionDetails():

    def __init__(self, osmId1, osmId2, ways1, ways2,azimuthintersectionstartway1,
                                                    azimuthintersectionendway1,
                                                    azimuthintersectionstartway2,
                                                    azimuthintersectionendway2,
                                                    azimuthbandstartway1,
                                                    azimuthbandendway1,
                                                    azimuthbandstartway2,
                                                    azimuthbandendway2,
                                                    matchedpoint):
        self.osmId1 = osmId1
        self.osmId2 = osmId2
        self.ways1 = None
        self.ways2 = None
        self.azimuthintersectionstartway1 = azimuthintersectionstartway1
        self.azimuthintersectionendway1 = azimuthintersectionendway1
        self.azimuthintersectionstartway2 = azimuthintersectionstartway2
        self.azimuthintersectionendway2 = azimuthintersectionendway2
        self.azimuthbandstartway1 = azimuthbandstartway1
        self.azimuthbandendway1 = azimuthbandendway1
        self.azimuthbandstartway2 = azimuthbandstartway2
        self.azimuthbandendway2 = azimuthbandendway2
        self.matchedpoint = matchedpoint



