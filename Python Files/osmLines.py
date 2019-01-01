import sys
from asynchat import async_chat
from math import sin, cos, sqrt, atan2, radians,degrees
import osmLinesQuery

#contains the lines matched with osmLines are carDetails
class CarToLines():
    def __init__(self,carDetails,osmLines):
        self.carDetails = carDetails
        self.osmLines = osmLines
        self.finalWay = []
        self.nextIntersection = []

    #assuming car is on the path we need to find the car position
    #based on direction.
    def findPathUsingCarLines(self):
        index = -1
        try:
            index = self.osmLines.way.index(self.carDetails.carPosition)
        except:
            index = -1
            print 'No Path was Found'
            return


class MyError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class SelectedLineObj():
    def __init__(self,osmLineId,matchedCoOrdinate,previousOsmLineId):
        self.osmLineId = osmLineId
        self.matchedCoOrdinate = matchedCoOrdinate
        self.previousOsmLineId = previousOsmLineId

#has information about car.
#This need to be updated as the car moves.
#
class CarDetails():
    def __init__(self,carPosition, carAzimuthAngle,carNextAzimuthAngle):
        self.carPosition = carPosition
        self.carAzimuthAngle = carAzimuthAngle
        self.previousPos = None
        self.previousAngleRange = None
        self.carNextAzimuthAngle = carNextAzimuthAngle
    def getCarPoistionAsPoint(self):
        return 'POINT('+self.carPosition+')'

    def setCarPosition(self,coOrd):
        self.carPosition = coOrd

    def removeFirstAngle(self):
        return self.carNextAzimuthAngle.pop(0)

#has information about lines
class OsmLines():
    def __init__(self,osmId,highwayType,roadName,way):
        self.osmId = osmId
        self.highwayType = highwayType
        self.roadName = roadName
        self.way = getIndividualCoOrdLines(way)
        self.azimuthBand = calculateMinAndMaxAzimuthAnglesofWay(self.way)

class MatchingRoads():
    def __init__(self,parent,osmId1,osmId2,matchedPoint):
        self.parent = parent
        self.osmId1 = osmId1 # first road osmid
        self.osmId2 = osmId2 # second one previous osmId
        self.matchedPoint = getIndividualCoOrdPoints(matchedPoint)
        self.anglesNotMatched = None

    def checkWithCarsHeading(self,carDetails):
        if getNSEWQuadrant(carDetails.carAzimuthAngle) == getNSEWQuadrant(calculateAzimuthAngle(carDetails.carPosition,self.matchedPoint)):
            return True
        else:
            return False
    def setMatchingPoint(self,matchingPoint):
        self.matchedPoint = matchingPoint

class IntersectionNodes:
    def __init__(self,parent,objectData,carObject):
        self.parent = parent
        self.objectData = objectData
        self.childrens = []
        self.carObject = carObject

    def addChildrens(self,objectToAdd):
        self.childrens.append(objectToAdd)

class NextRoadForIntersection:
    def __init__(self,osmId,carObj):
        self.osmId = osmId
        self.carObj = carObj

class IntersectionDetails():
    def __init__(self,osmId1,osmId2,intersectionPoint,distanceToIntersection):
        self.osmId1 = osmId1
        self.osmId2 = osmId2
        self.intersectionPoint =  getIndividualCoOrdPoints(intersectionPoint)
        self.distanceToIntersection = distanceToIntersection
        self.distaceToNearestPoint = None
        self.nearestPoint = None
        self.nearestPointOsmLineId = None

    def getNonMatchedOsmId(self):
        if self.nearestPointOsmLineId == self.osmId1:
            return self.osmId2
        if self.nearestPointOsmLineId == self.osmId2:
            return self.osmId1
        return None

    def generateNearestRoadPoint(self,cursor,carObj,logging):

        carPosition = carObj.carPosition

        cursor.execute(osmLinesQuery.osmLineQuery,(self.osmId1,))
        row = cursor.fetchone()
        ways = getIndividualCoOrdLines(row[3])
        minDist = sys.maxint
        for coOrd in ways:
            distance = calculateDistance(coOrd,carPosition)
            if distance < minDist:
                minDist = distance
                angleVal = False
                index = ways.index(coOrd)
                try:
                    nextCoord = ways[index+1]
                    angle = calculateAzimuthAngle(coOrd,nextCoord)
                    if not((getNSEWQuadrant(angle) == getNSEWQuadrant(carObj.carAzimuthAngle)) or getNSEWQuadrant(angle) == getNSEWQuadrant((carObj.carAzimuthAngle+180)%360)):
                        angleVal = False
                    else:
                        angleVal = True
                except:
                    logging.error('index + 1 not available')
                    angleVal = False
                try:
                    prevCoord = ways[index-1]
                    angle = calculateAzimuthAngle(coOrd, prevCoord)
                    if not((getNSEWQuadrant(angle) == getNSEWQuadrant(carObj.carAzimuthAngle)) or getNSEWQuadrant(angle) == getNSEWQuadrant((carObj.carAzimuthAngle+180)%360)):
                        angleVal = False
                    else:
                        angleVal = True
                except:
                    logging.error('index - 1 not available')
                    angleVal = False
                if angleVal:
                    self.nearestPoint = coOrd
                    self.distaceToNearestPoint = distance
                    self.nearestPointOsmLineId = self.osmId1
                else:
                    continue

        cursor.execute(osmLinesQuery.osmLineQuery, (self.osmId2,))
        row = cursor.fetchone()
        ways = getIndividualCoOrdLines(row[3])
        for coOrd in ways:
            distance = calculateDistance(coOrd, carPosition)
            if distance < minDist:
                minDist = distance
                self.nearestPoint = coOrd
                self.distaceToNearestPoint = distance
                self.nearestPointOsmLineId = self.osmId2


########################################################################################################################
def getIndividualCoOrdPoints(gpsCord):
    if gpsCord is not None:
        coOrd = gpsCord[6:-1]
        return coOrd
    else:
        return

def getIndividualCoOrdLines(roadsGPS):

    coOrdWays = roadsGPS[11:-1]
    #print coOrdWays
    splitCordWays = coOrdWays.split(",")
    return splitCordWays

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
    #print 'List of angles ',listOfAngles
    maxDelta = -1
    startAngle =0
    endAngle = 0
    lenOfangles = len(listOfAngles)
    if lenOfangles == 1:
        return listOfAngles[0],listOfAngles[0]

    for i in range(0,lenOfangles-1):
        for j in range(0,lenOfangles-1):
            delta = calculateDeltaBetweenAngles(listOfAngles[i],listOfAngles[j])
            if(delta > maxDelta):
                maxDelta = delta
                startAngle = min(listOfAngles[i],listOfAngles[j])
                endAngle = max(listOfAngles[i],listOfAngles[j])

    #print 'max delta obtained ',maxDelta, startAngle,endAngle
    return startAngle,endAngle

def calculateAzimuthAngle(gps1,gps2):
    #input '-71.09725 42.3316','-71.09738 42.33132'

    lat1 = float(gps1.split(" ")[1])
    lon1 = float(gps1.split(" ")[0])
    lat2 = float(gps2.split(" ")[1])
    lon2 = float(gps2.split(" ")[0])


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
    if angle >= 337.25 or angle < 22.5:
        return 'N'
    if angle >= 292.5 and angle < 337.25:
        return 'NW'
    if angle >= 247.5 and angle < 292.5:
        return 'W'
    if angle >= 202.5 and angle < 247.5:
        return 'SW'
    if angle >= 157.5 and angle < 202.5:
        return 'S'
    if angle >= 112.5 and angle < 157.5:
        return 'SE'
    if angle >= 67.5 and angle < 112.5:
        return 'E'
    if angle >= 22.5 and angle < 67.5:
        return 'NE'

def getNSEWQuadrantWithRange(angle):
    if angle >= 337.25 or angle < 22.5:
        return 'N',(337,22.4)
    if angle >= 292.5 and angle < 337.25:
        return 'NW',(292.5,337.24)
    if angle >= 247.5 and angle < 292.5:
        return 'W',(247.5,292.4)
    if angle >= 202.5 and angle < 247.5:
        return 'SW',(202.5,247.4)
    if angle >= 157.5 and angle < 202.5:
        return 'S',(157.5,202.4)
    if angle >= 112.5 and angle < 157.5:
        return 'SE',(112.5,157.4)
    if angle >= 67.5 and angle < 112.5:
        return 'E',(67.5,112.4)
    if angle >= 22.5 and angle < 67.5:
        return 'NE',(22.5,67.4)


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


    return towardsDirection

def findAllGpsCoOrdBetweenPoints(roadLine,matchedPointFrom,matchedPointTo,finalPathCoOrd,logging):


    indexFrom = roadLine.index(matchedPointFrom)
    indexTo = roadLine.index(matchedPointTo)
    logging.debug('index from : index to'+str(indexFrom)+':'+str(indexTo))
    if indexFrom < indexTo:
        for i in range(indexFrom,indexTo+1):
            finalPathCoOrd.append(roadLine[i])
    else:
        for i in range(indexTo,indexFrom+1):
            finalPathCoOrd.append(roadLine[i])

    return finalPathCoOrd




def specialAppend(routeStack,elem):
    if isinstance(elem, MatchingRoads):
        if elem not in routeStack:
            routeStack.append(elem)



def getNSEWQuadrantWithDelta(azimuthAngle,delta = 5):

    angleList = [azimuthAngle,azimuthAngle+delta,azimuthAngle-delta]
    possibleDirections = []
    for angle in angleList:
        if angle >= 337.25 or angle < 22.5:
            possibleDirections.append('N')
        if angle >= 292.5 and angle < 337.25:
            possibleDirections.append('NW')
        if angle >= 247.5 and angle < 292.5:
            possibleDirections.append('W')
        if angle >= 202.5 and angle < 247.5:
            possibleDirections.append('SW')
        if angle >= 157.5 and angle < 202.5:
            possibleDirections.append('S')
        if angle >= 112.5 and angle < 157.5:
            possibleDirections.append('SE')
        if angle >= 67.5 and angle < 112.5:
            possibleDirections.append('E')
        if angle >= 22.5 and angle < 67.5:
            possibleDirections.append('NE')

    return possibleDirections