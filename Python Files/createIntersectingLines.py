import sys
import psycopg2
import sets
from math import sin, cos, sqrt, atan2, radians, degrees
from decimal import *

def calculateDistance(gps1,gps2):

    lat1 = radians(float(gps1.split(" ")[1]))
    lon1 = radians(float(gps1.split(" ")[0]))
    lat2 = radians(float(gps2.split(" ")[1]))
    lon2 = radians(float(gps2.split(" ")[0]))

    R = 6373.0

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    #print("Result:", distance)
    return distance

def calculateAzimuthAngle(gps1,gps2):

    #print 'Calculating Azimuth Angle for Co-Ordinates ->',gps1,' : ',gps2
    lat1 = float(gps1.split(" ")[1])
    lon1 = float(gps1.split(" ")[0])
    lat2 = float(gps2.split(" ")[1])
    lon2 = float(gps2.split(" ")[0])

    # approximate radius of earth in km
    R = 6373.0

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    firstPart = sin(radians(dlon)) * cos(radians(lat2))
    lastpart = cos(radians(lat1)) * sin(radians(lat2)) - sin(radians(lat1))*cos(radians(lat2)) * cos(radians(dlon))
    theta = atan2(firstPart,lastpart)
    if degrees(theta) < 0:
        return 360 + degrees(theta)
    else:
        return degrees(theta)

def calculateDeltaBetweenAngles(anglex, angleY):
    maxAngle = max(anglex,angleY)
    minAngle = min(anglex,angleY)
    delta = None
    if maxAngle >= 270.00 and maxAngle < 360 and minAngle >=0 and minAngle <= 90:
        delta = 360 - (maxAngle - minAngle)
    else:
        delta = maxAngle - minAngle
    return delta

class MeetingWays:

    def __init__(self,osmId1,osmId2,ways1,ways2):
        self.osmId1 = osmId1
        self.osmId2 = osmId2
        self.ways1 = ways1
        self.ways2 = ways2
        self.matchedLines = []
        self.relation = None
        self.azimuthAngleIntersectionStartWay1 = 0.0
        self.azimuthAngleIntersectionStartWay2 = 0.0
        self.azimuthAngleIntersectionEndWay2 = 0.0
        self.azimuthAngleIntersectionEndWay1 = 0.0
        self.azimuthbandWay1 = (0.0,0.0)
        self.azimuthbandWay2 = (0.0,0.0)
        self.splitWays1 = []
        self.splitWays2 = []

    def getAzimuthIntersectionStartWay1(self):
        return self.azimuthAngleIntersectionStartWay1

    def getAzimuthIntersectionEndWay1(self):
        return self.azimuthAngleIntersectionEndWay1

    def getAzimuthIntersectionStartWay2(self):
        return self.azimuthAngleIntersectionStartWay2

    def getAzimuthIntersectionEndWay2(self):
        return self.azimuthAngleIntersectionEndWay2

    def getAzimuthbandWay1(self):
        return self.azimuthbandWay1

    def getAzimuthbandWay2(self):
        return self.azimuthbandWay2

    def getMatchedLines(self):

        if len(self.matchedLines) > 0 and len(self.matchedLines) == 1:
            return str(self.matchedLines[0])
        elif len(self.matchedLines) > 1:
            return self.getMatchedLinesAsStr()

    def getMatchedLinesCount(self):
        return len(self.matchedLines)

    def getMatchedLinesAsStr(self):
        print 'returning multiple matched points'
        matchedStr = "'LINESTRING("
        for match in self.matchedLines:
            matchedStr =matchedStr +match+ ","

        return matchedStr+")'"

    def getWays1(self):
        return self.ways1

    def getWays2(self):
        return self.ways2

    def getOsmId1(self):
        return self.osmId1

    def getOsmId2(self):
        return self.osmId2



    def compareTwoWays(self):
        lenWays1 = len(self.ways1)
        lenWays2 = len(self.ways2)

        coOrdWays1 = self.ways1[11:lenWays1 - 1]
        coOrdWays2 = self.ways2[11:lenWays2 - 1]

        #print 'Comparing co ordinates ',coOrdWays1
        #print 'Comparing co ordinates ', coOrdWays2

        splitCordWays1 = coOrdWays1.split(",")
        self.splitWays1 = splitCordWays1
        splitCordWays2 = coOrdWays2.split(",")
        self.splitWays2 = splitCordWays2


        for coOrd1 in splitCordWays1:
            if(coOrd1 in splitCordWays2):
                self.matchedLines.append(coOrd1)
                #print 'Matched Co-Ord ', coOrd1
            elif (self.distanceCord(coOrd1,splitCordWays2)) <=  0.00001:
                self.matchedLines.append(coOrd1)
                #print 'Matched Co-Ord ',coOrd1

    def distanceCord(self,coOrd1,splitCordWays):
        for coOrd2 in splitCordWays:
            return calculateDistance(coOrd1,coOrd2)

    #TO_DO works for single matched co ordinates between two lines. Assumption for now.
    def findAzimuthAnglesOSM1(self):
        #indexOfIntersection = self.splitWays1.index(self.matchedLines[0])
        #print 'INDEX OF INTERSECTION ',indexOfIntersection , ' : with values ',self.matchedLines[0]
        #if indexOfIntersection > 0:
        #    self.azimuthAngleIntersectionStartWay1 = calculateAzimuthAngle(self.splitWays1[indexOfIntersection-1],self.matchedLines[0])
        #    self.azimuthAngleIntersectionEndWay1 = calculateAzimuthAngle(self.matchedLines[0],self.splitWays1[indexOfIntersection+1])
        #else:
        #    self.azimuthAngleIntersectionStartWay1 = calculateAzimuthAngle(self.splitWays1[indexOfIntersection],
        #                                                               self.matchedLines[0])
        #    self.azimuthAngleIntersectionEndWay1 = calculateAzimuthAngle(self.matchedLines[0], self.splitWays1[indexOfIntersection + 1])
        min, max = self.calculateMinAndMaxAzimuthAnglesofWay(self.splitWays1)
        self.azimuthbandWay1 = (min,max)
        #print 'Completed way1 calculations'


    def findAzimuthAnglesOSM2(self):
        indexOfIntersection = -1
        #try:
        #    indexOfIntersection = self.splitWays2.index(self.matchedLines[0])
        #except:
        #    indexOfIntersection = -1

        #if indexOfIntersection != -1:
        #    lenOfWay = len(self.splitWays2)
        #    if indexOfIntersection == (lenOfWay-1):
        #        self.azimuthAngleIntersectionStartWay2 = calculateAzimuthAngle(self.ways2(indexOfIntersection-1),self.matchedLines[0])
        #        self.azimuthAngleIntersectionEndWay2 = calculateAzimuthAngle(self.ways2)
        #    if indexOfIntersection == 0:
        #        self.azimuthAngleIntersectionStartWay2 = calculateAzimuthAngle(self.ways2(indexOfIntersection),self.ways2(indexOfIntersection + 1))

        min, max = self.calculateMinAndMaxAzimuthAnglesofWay(self.splitWays2)
        self.azimuthbandWay2 = (min,max)
        #print 'Completed way2 calculations'

    def calculateMinAndMaxAzimuthAnglesofWay(self,ways):

        previousValue = None
        listOfAngles = []
        for coOrd in ways:
            if previousValue is not None:
                angle = calculateAzimuthAngle(coOrd, previousValue)
                listOfAngles.append((angle + 180) % 360)
                previousValue = coOrd
            else:
                previousValue = coOrd
        #print 'List of angles ',listOfAngles
        maxDelta = -1
        startAngle =0
        endAngle = 0
        lenOfangles = len(listOfAngles)
        for i in range(0,lenOfangles-1):
            for j in range(0,lenOfangles-1):
                delta = calculateDeltaBetweenAngles(listOfAngles[i],listOfAngles[j])
                if(delta > maxDelta):
                    maxDelta = delta
                    startAngle = min(listOfAngles[i],listOfAngles[j])
                    endAngle = max(listOfAngles[i],listOfAngles[j])

        #print 'max delta obtained ',maxDelta, startAngle,endAngle
        return startAngle,endAngle

def addToListByComparison(osmId1,osmId2,list):
    list.append((osmId1,osmId2))
    list.append((osmId2, osmId1))


def findIntersectingLines():
    meetingWays = []
    listOfMatchedOsmIds = []
    conn = psycopg2.connect("dbname=osm user=praveen password=postgres")
    cursor = conn.cursor()

    clearIntersectionTable = """truncate table planet_osm_intersecting_lines;"""

    cursor.execute(clearIntersectionTable)

    intersectSQL =  """
                    select osml1.osm_id,osml2.osm_id,ST_AsText(ST_Transform(osml1.way, 4326)) "way1",ST_AsText(ST_Transform(osml2.way, 4326)) "way2" 
                    from planet_osm_line osml1, planet_osm_line osml2
                    where ST_Intersects(osml1.way,osml2.way)
                    and osml1.highway not in ('footway','cycleway','service')
                    and osml2.highway not in ('footway','cycleway','service')
					and osml1.osm_id > 0
					and osml2.osm_id > 0
					and osml1.osm_id != osml2.osm_id;
                    """
    cursor.execute(intersectSQL)
    row = cursor.fetchone()

    while row is not None:
        #print 'Intersecting lines ',row
            #print 'Loading meeting ways'
            meetingObj = MeetingWays(row[0],row[1],row[2],row[3])
            meetingWays.append(meetingObj)
            row = cursor.fetchone()
            continue

    cursor.close()

    print 'Meeting roads are ',meetingWays

    cursor = conn.cursor()
    for ways in meetingWays:
        ways.compareTwoWays()
        ways.findAzimuthAnglesOSM1()
        ways.findAzimuthAnglesOSM2()
        if ways.getMatchedLines() == None:
            continue
        if (ways.osmId1,ways.osmId2) in listOfMatchedOsmIds:
            continue
        print 'OSMID1 ' +str(ways.getOsmId1()) + ' : OSMID2 '+str(ways.getOsmId2())
        print 'Matched POINT' , ways.getMatchedLines(), ' band of values ',ways.getAzimuthbandWay1()

        #if len(ways.matchedLines) > 1:
        addToListByComparison(ways.osmId1,ways.osmId2,listOfMatchedOsmIds)
        cursor.callproc('userProc_add_intersecting_lines', (ways.getOsmId1(),
                                                            ways.getOsmId2(),
                                                            Decimal(ways.getAzimuthIntersectionStartWay1()),
                                                            Decimal(ways.getAzimuthIntersectionEndWay1()),
                                                            Decimal(ways.getAzimuthIntersectionStartWay2()),
                                                            Decimal(ways.getAzimuthIntersectionEndWay2()),
                                                            Decimal(ways.getAzimuthbandWay1()[0]),
                                                            Decimal(ways.getAzimuthbandWay1()[1]),
                                                            Decimal(ways.getAzimuthbandWay2()[0]),
                                                            Decimal(ways.getAzimuthbandWay2()[1]),
                                                            ways.getMatchedLines()))


    conn.commit()
    cursor.close()
    conn.close()


findIntersectingLines()











