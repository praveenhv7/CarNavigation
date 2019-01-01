from math import sin, cos, sqrt, atan2, radians, degrees
import sys

class TravelDetails():

    def __init__(self,
                    travelId,
                    osmId1,
                    osmId2,
                    azimuthintersectionstartway1,
                    azimuthintersectionendway1,
                    azimuthintersectionstartway2,
                    azimuthintersectionendway2,
                    azimuthbandstartway1,
                    azimuthbandendway1,
                    azimuthbandstartway2,
                    azimuthbandendway2,
                    matchedpoint,
                    travelOsmId
                    ):
        self.travelId = travelId
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
        self.matchedpoint = getIndividualCoOrdPoints(matchedpoint)
        self.travelOsmId = travelOsmId
        self.carGPSOnRoad = None

    def findNonTravelledOSMId(self):
        if self.travelOsmId == self.osmId1:
            return self.osmId2
        elif self.travelOsmId == self.osmId2:
            return self.osmId1

    def toString(self):
        objStr = "travelID :"+str(self.travelId)+"\n" \
            "osmid1 :" + str(self.osmId1) +"\n" \
            "osmid2 :" + str(self.osmId2) + "\n" \
            "azimuthintersectionstartway1: " + str(self.azimuthintersectionstartway1) + "\n" \
            "azimuthintersectionendway1: " + str(self.azimuthintersectionendway1) + "\n" \
            "azimuthintersectionstartway2: " + str(self.azimuthintersectionstartway2) + "\n" \
            "azimuthintersectionendway2: " + str(self.azimuthintersectionendway2) + "\n" \
            "azimuthbandstartway1: " + str(self.azimuthbandstartway1) + "\n" \
            "azimuthbandendway1: " + str(self.azimuthbandendway1) + "\n" \
            "azimuthbandstartway2: " + str(self.azimuthbandstartway2) + "\n" \
            "azimuthbandendway2: " + str(self.azimuthbandendway2) + "\n" \
            "matchedpoint: " + str(self.matchedpoint) + "\n" \
            "ways1 "+str(self.ways1) + "\n" \
            "ways2 " + str(self.ways2) + "\n"\
            "travelOSMId :"+str(self.travelOsmId)
        print objStr


class OSMLinesDetails():
    def __init__(self,osmId,highwayType,roadName,way):
        self.osmId = osmId
        self.highwayType = highwayType
        self.roadName = roadName
        self.way = getIndividualCoOrdLines(way)
        self.azimuthBand = calculateMinAndMaxAzimuthAnglesofWay(self.way)
        self.wayAftercarLoc = []
        self.waybeforecarLoc = []
        self.angleAfterCarLoc = None
        self.angleBeforeCarLoc = None
        self.azimuthBandAfterCarLoc = None
        self.azimuthBandBeforeCarLoc = None
        self.nextIntersection = None
        self.wayToIntersection = None
        self.azimuthBandToIntersection = None
        self.toIntersectionAzimuthStart = None
        self.azimuthStartIntersect = None

    def extractWayAfterBeforeCarLoc(self,carLoc):
        index = self.way.index(carLoc)
        self.wayAftercarLoc = self.way[index+1:]
        self.waybeforecarLoc = self.way[:index]
        if len(self.wayAftercarLoc) > 0:
            self.angleAfterCarLoc = calculateAzimuthAngle(carLoc,self.wayAftercarLoc[0])
            self.azimuthBandAfterCarLoc = calculateMinAndMaxAzimuthAnglesofWay(self.wayAftercarLoc)
        if len(self.waybeforecarLoc) > 0:
            self.angleBeforeCarLoc = calculateAzimuthAngle(carLoc,self.waybeforecarLoc[-1])
            self.azimuthBandBeforeCarLoc = calculateMinAndMaxAzimuthAnglesofWay(self.waybeforecarLoc)
        self.wayAftercarLoc.insert(0,carLoc)
        self.waybeforecarLoc.append(carLoc)

    def setNextIntersection(self,intersection,carPosition):
        self.nextIntersection = intersection
        indexIntersect = self.way.index(intersection)
        indexCarPos = self.way.index(carPosition)

        if indexIntersect > indexCarPos:
            self.wayToIntersection = self.way[indexCarPos:indexIntersect]
            self.azimuthBandToIntersection = calculateMinAndMaxAzimuthAnglesofWay(self.wayToIntersection)
            self.azimuthStartIntersect = calculateAzimuthAngle(self.wayToIntersection[indexCarPos],self.wayToIntersection[indexCarPos+1])
        else:
            self.wayToIntersection = self.way[indexIntersect:indexCarPos]
            self.azimuthBandToIntersection = calculateMinAndMaxAzimuthAnglesofWay(self.wayToIntersection)


    def toString(self):
        strObj = "self.osmId :" + str(self.osmId)+ "\n"\
                 "self.highwayType :" +str(self.highwayType) +"\n"\
                 "self.roadName :" +str(self.roadName)+"\n"\
                 "self.way :" + str(self.way)+"\n" \
                 "self.azimuthBand :" + str(self.azimuthBand) + "\n"\
                "self.wayAftercarLoc :" + str(self.wayAftercarLoc) + "\n"\
                "self.waybeforecarLoc :" + str(self.waybeforecarLoc) + "\n"\
                "self.angleAfterCarLoc :" + str(self.angleAfterCarLoc) + "\n"\
                "self.angleBeforeCarLoc :" + str(self.angleBeforeCarLoc) + "\n"\
                "self.azimuthBandAfterCarLoc :" + str(self.azimuthBandAfterCarLoc) + "\n"\
                "self.azimuthBandBeforeCarLoc :" + str(self.azimuthBandBeforeCarLoc) + "\n"
        print strObj

class IntersectionToNextIntersection():
    def __init__(self,osmId,highwayType,name,way,azimuthintersectionstartway,azimuthintersectionendway,azimuthbandstartway,azimuthbandendway,matchedPoint):
        self.osmId = osmId
        self.highwayType = highwayType
        self.name = name
        self.way = way
        self.azimuthintersectionstartway = azimuthintersectionstartway
        self.azimuthintersectionendway = azimuthintersectionendway
        self.azimuthbandstartway = azimuthbandstartway
        self.azimuthbandendway = azimuthbandendway
        self.matchedPoint = matchedPoint

class CarDetails():

    def __init__(self,carGPS,heading):
        self.gpsCoOrdinates = carGPS
        self.heading = heading
        #prefill this with valid values. this is a queue to be used after reaching intersection
        self.turns = ['Left']
        self.closestRoadDistance = sys.maxint
        self.closestRoadOsmIds = []

    def toString(self):
        output = "gps co-ordinates "+ self.gpsCoOrdinates +"\n" \
                 "heading direction "+ str(self.heading) +"\n"
        print output

def getIndividualCoOrdPoints(gpsCord):
    coOrd = gpsCord[6:-1]
    return coOrd

def getIndividualCoOrdLines(roadsGPS):

    coOrdWays = roadsGPS[11:-1]
    print coOrdWays
    splitCordWays = coOrdWays.split(",")
    return splitCordWays


def calculateMinAndMaxAzimuthAnglesofWay(ways):

    previousValue = None
    listOfAngles = []
    for coOrd in ways:
        if previousValue is not None:
            angle = calculateAzimuthAngle(coOrd, previousValue)
            listOfAngles.append((angle + 180) % 360)
            previousValue = coOrd
        else:
            previousValue = coOrd
    print 'List of angles ',listOfAngles
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

    print 'max delta obtained ',maxDelta, startAngle,endAngle
    return startAngle,endAngle

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

def getNSEWQuadrant(angle):
    if angle > 337.25 or angle < 22.5:
        return 'N'
    if angle > 292.5 and angle < 337.25:
        return 'NW'
    if angle > 247.5 and angle < 292.5:
        return 'W'
    if angle > 202.5 and angle < 247.5:
        return 'SW'
    if angle > 157.5 and angle < 202.5:
        return 'S'
    if angle > 112.5 and angle < 157.5:
        return 'SE'
    if angle > 67.5 and angle < 112.5:
        return 'E'
    if angle > 22.5 and angle < 67.5:
        return 'NE'

def addSelectedPOStoTravelMap(selectedRoadList,roadTakenMap,carDirection):

    for selectedRoad in selectedRoadList:
        roadTakenMap.update({selectedRoad.roadOsmID:[]})
        for roadCoord in selectedRoad.ways:
            # if getNSEWQuadrant(calculateAzimuthAngle(roadCoord,selectedRoad.coOrdinate)) == carDirection:

            roadCoordlat = float(roadCoord.split(" ")[1])
            roadCoordlon = float(roadCoord.split(" ")[0])
            nearestCoOrdlat = float(selectedRoad.coOrdinate.split(" ")[1])
            nearestCoOrdlon = float(selectedRoad.coOrdinate.split(" ")[0])
            intersectionCoOrdlat = float(selectedRoad.intersectionCoOrd.split(" ")[1])
            intersectionCoOrdlon = float(selectedRoad.intersectionCoOrd.split(" ")[0])

            if carDirection == 'NW':
                # Movement towards North increases latitude
                # Movement towards west decreases longitude
                if (
                        roadCoordlat >= nearestCoOrdlat and roadCoordlon <= nearestCoOrdlon and roadCoordlat <= intersectionCoOrdlat and roadCoordlon >= intersectionCoOrdlon):
                    roadTakenMap.get(selectedRoad.roadOsmID).append(roadCoord)
            if carDirection == 'N':
                # Movement towards North increases latitude.
                if (roadCoordlat >= nearestCoOrdlat and roadCoordlat <= intersectionCoOrdlat):
                    roadTakenMap.get(selectedRoad.roadOsmID).append(roadCoord)
            if carDirection == 'NE':
                # Movement towards North increases latitude.
                # Movement towards East increases longitude.
                if (
                        roadCoordlat >= nearestCoOrdlat and roadCoordlon >= nearestCoOrdlon and roadCoordlat <= intersectionCoOrdlat and roadCoordlon <= intersectionCoOrdlon):
                    roadTakenMap.get(selectedRoad.roadOsmID).append(roadCoord)
            if carDirection == 'SW':
                # Movement towards south decreases latitude.
                # movement towards west decreases longitude
                if (
                        roadCoordlat <= nearestCoOrdlat and roadCoordlon <= nearestCoOrdlon and roadCoordlat >= intersectionCoOrdlat and roadCoordlon >= intersectionCoOrdlon):
                    roadTakenMap.get(selectedRoad.roadOsmID).append(roadCoord)
            if carDirection == 'S':
                # Movemennt towards south decreases latitude.
                if (roadCoordlat <= nearestCoOrdlat and roadCoordlat >= intersectionCoOrdlat):
                    roadTakenMap.get(selectedRoad.roadOsmID).append(roadCoord)
            if carDirection == 'SE':
                # Movement towards south decreases latitude.
                # Movement towards east increases longitude.
                if (
                        roadCoordlat <= nearestCoOrdlat and roadCoordlon >= nearestCoOrdlon and roadCoordlat >= intersectionCoOrdlat and roadCoordlon <= intersectionCoOrdlon):
                    roadTakenMap.get(selectedRoad.roadOsmID).append(roadCoord)
            if carDirection == 'E':
                # Movement towards east increases longitude.
                if (roadCoordlon >= nearestCoOrdlon and roadCoordlon <= intersectionCoOrdlon):
                    roadTakenMap.get(selectedRoad.roadOsmID).append(roadCoord)
            if carDirection == 'W':
                # Movement towards west decreases longitude.
                if (roadCoordlon <= nearestCoOrdlon and roadCoordlon >= intersectionCoOrdlon):
                    roadTakenMap.get(selectedRoad.roadOsmID).append(roadCoord)


    print 'road taken ', roadTakenMap


class CarToRoad():

    def __init__(self,osmId,distance,coOrdinate,azimuthStart,azimuthEnd,ways,intersectionCoOrd):
        self.roadOsmID = osmId
        self.distance = distance
        self.coOrdinate = coOrdinate
        self.roadAzimuthStart = azimuthStart
        self.roadAzimuthEnd = azimuthEnd
        self.ways = ways
        self.intersectionCoOrd = intersectionCoOrd


def findPosTowardsCarDirection(selectedRoadList, carDirection, matchedPoint):
    towardsDirection = []
    for roadCoord in selectedRoadList:
        # if getNSEWQuadrant(calculateAzimuthAngle(roadCoord,selectedRoad.coOrdinate)) == carDirection:
        roadCoordlat = float(roadCoord.split(" ")[1])
        roadCoordlon = float(roadCoord.split(" ")[0])
        nearestCoOrdlat = float(matchedPoint.split(" ")[1])
        nearestCoOrdlon = float(matchedPoint.split(" ")[0])

        if carDirection == 'NW':
            # Movement towards North increases latitude
            # Movement towards west decreases longitude
            if (roadCoordlat >= nearestCoOrdlat and roadCoordlon <= nearestCoOrdlon ):
                towardsDirection.append(roadCoord)
        if carDirection == 'N':
            # Movement towards North increases latitude.
            if (roadCoordlat >= nearestCoOrdlat):
                towardsDirection.append(roadCoord)
        if carDirection == 'NE':
            # Movement towards North increases latitude.
            # Movement towards East increases longitude.
            if (roadCoordlat >= nearestCoOrdlat and roadCoordlon >= nearestCoOrdlon ):
                towardsDirection.append(roadCoord)
        if carDirection == 'SW':
            # Movement towards south decreases latitude.
            # movement towards west decreases longitude
            if (roadCoordlat <= nearestCoOrdlat and roadCoordlon <= nearestCoOrdlon ):
                towardsDirection.append(roadCoord)
        if carDirection == 'S':
            # Movemennt towards south decreases latitude.
            if (roadCoordlat <= nearestCoOrdlat):
                towardsDirection.append(roadCoord)
        if carDirection == 'SE':
            # Movement towards south decreases latitude.
            # Movement towards east increases longitude.
            if (roadCoordlat <= nearestCoOrdlat and roadCoordlon >= nearestCoOrdlon ):
                towardsDirection.append(roadCoord)
        if carDirection == 'E':
            # Movement towards east increases longitude.
            if (roadCoordlon >= nearestCoOrdlon ):
                towardsDirection.append(roadCoord)
        if carDirection == 'W':
            # Movement towards west decreases longitude.
            if (roadCoordlon <= nearestCoOrdlon ):
                towardsDirection.append(roadCoord)

    logging.debug( 'road taken '+ towardsDirection)
    return towardsDirection