from math import sin, cos, sqrt, atan2, radians, degrees
import sys
import Queue
from osmLines import *
import logging
import osmLinesQuery
import psycopg2
import copy
from collections import OrderedDict

#############################################################


##############################################################
#takes the initial position and gets the
#nearest road matching the azimuth.
def findTheRoadMatchingCarPosition(carObj):

    direction, range = getNSEWQuadrantWithRange(carObj.carAzimuthAngle)
    carObj.previousAngleRange = range
    logging.debug(range[1])
    cursor.execute(osmLinesQuery.intersectionSQL,(carObj.carPosition,carObj.carPosition,range[0],range[1],))
    row = cursor.fetchone()
    nearestPositions = []
    while row is not None:
        intersectionObj = IntersectionDetails(row[0],row[1],row[2],row[3])
        intersectionObj.generateNearestRoadPoint(cursor,carObj,logging)
        nearestPositions.append(intersectionObj)
        logging.debug(row)
        row = cursor.fetchone()

    min = sys.maxint
    finalIntersectionObj = None
    for obj in nearestPositions:
        distance = obj.distaceToNearestPoint
        if distance < min:
            min = distance
            finalIntersectionObj = obj
    logging.debug('Position selected'+str(finalIntersectionObj.nearestPoint))
    #return finalIntersectionObj
    matchedRoad = MatchingRoads(None, finalIntersectionObj.nearestPointOsmLineId, finalIntersectionObj.getNonMatchedOsmId(),None )
    matchedRoad.setMatchingPoint(finalIntersectionObj.nearestPoint)
    return matchedRoad


def findTheNextIntersectionsToTurn(matchedRoad,carObj,parentNode,listOfChildrens):

    # find the intersections from the available osmids which were returned
    # using the available mappedRoadObject of type intersection details
    # find all intersections for this osmId.

    logging.debug('Printing Details')
    logging.debug('osmId1 :'+str(matchedRoad.osmId1))
    logging.debug('osmId2 :'+str(matchedRoad.osmId2))
    logging.debug('Matched Point '+str(matchedRoad.matchedPoint))

    intersections = getIntersectionRelatedToOSMId(carObj.carPosition,matchedRoad.osmId1,matchedRoad.osmId2,carObj.previousAngleRange)
    carObj.setCarPosition(matchedRoad.matchedPoint)
    newCarObj = copy.deepcopy(carObj)

    for intersection in intersections:
        logging.debug(intersection.osmId2)

        logging.debug('Cars available angle '+ str(newCarObj.carNextAzimuthAngle))
        nextNode = IntersectionNodes(parentNode, intersection, newCarObj)
        retObj = recursiveFindOtherMatches(nextNode,newCarObj,listOfChildrens)
        listOfChildrens.append(retObj)
        logging.debug("***********End of One Intersection*************")


def printDictionary(dict):
    logging.debug("Route 1")
    for myKey in dict.keys():

        logging.debug(dict[myKey].osmId1)
        logging.debug(dict[myKey].osmId2)
        logging.debug(dict[myKey].matchedPoint)


def printCollection(allTraveledPaths):
    logging.debug(allTraveledPaths)
    # childNode = allTraveledPaths.get(619015494L)
    # while childNode.parent is not None:
    #    logging.debug(childNode.objectData.osmId1)
    #    childNode = childNode.parent


#1. Take an intersection point as a object find the other lines
#   Find the lines that match the car's first azimuth (To - Do)
#   once it matches get the osmID and find for other intersections by passing osmId to the function.
#  this function again returns the next intersections related to that line ...
#
#
def recursiveFindOtherMatches(parentNode,carObj,allTraveledPaths):
    #for the available turns we will find the next available intersections
    intersectionDetail = parentNode.objectData
    logging.debug(intersectionDetail)
    logging.debug(intersectionDetail.osmId1)
    logging.debug(intersectionDetail.osmId2)
    logging.debug(intersectionDetail.matchedPoint)

    if intersectionDetail.osmId2 < 0:
        return parentNode

    if len(carObj.carNextAzimuthAngle) == 0:
        logging.debug("No More Angles left : Returning")

        newCarObject = copy.deepcopy(carObj)
        nextNode = IntersectionNodes(parentNode,None,newCarObject)
        parentNode.addChildrens(nextNode)
        return parentNode

    else:
        logging.debug("check if the line matches cars azimuth")
        newCarObj = copy.deepcopy(carObj)
        angle = newCarObj.carNextAzimuthAngle[0]
        logging.debug('obtained angle '+str(angle))
        intersectionDetail = parentNode.objectData
        lineDetailsObj = getLineDetails(intersectionDetail.osmId2,intersectionDetail.matchedPoint)
        validDirection = carDirectionFunction(lineDetailsObj,angle,intersectionDetail.matchedPoint)
        if validDirection:
            angle = newCarObj.removeFirstAngle()
            newCarObj.previousAngleRange = getNSEWQuadrantWithRange(angle)[1]
            logging.debug("previous angle stored " +str(newCarObj.previousAngleRange))
            logging.debug("remaining angle")
            logging.debug(newCarObj.carNextAzimuthAngle)
            newCarObj.setCarPosition(intersectionDetail.matchedPoint)
            matchingRoad = MatchingRoads(None,lineDetailsObj.osmId,intersectionDetail.osmId1,None)
            matchingRoad.setMatchingPoint(intersectionDetail.matchedPoint)
            newCarObject = copy.deepcopy(carObj)
            nextNode = IntersectionNodes(parentNode,matchingRoad,newCarObject)
            parentNode.addChildrens(matchingRoad)
            #startSearchForIntersections([],newCarObj,selectedLineObj,nextNode,allTraveledPaths)
            findTheNextIntersectionsToTurn(matchingRoad,newCarObj,nextNode,allTraveledPaths)
        else:
            logging.debug("Couldn Find valid road")
            #carObj.removeFirstAngle()
            return parentNode
    logging.debug('THIS SHOULDN HAPPEN')
    return parentNode

def getIntersectionRelatedToOSMId(carPosition,osmId,previousOsmId,angleRange):
    logging.debug("Get Line Intersection Details for "+str(osmId) +" and " +str(previousOsmId))
    logging.debug("car poistion "+str(carPosition))
    listOfAllIntersections = []
    lowerRange = (angleRange[0] - 45)%360
    higherRange = (angleRange[1] + 45)%360

    azimuthFilter = '''where "degrees" >=%s
                       AND "degrees" <=%s'''

    azimuthFilterModified = '''where "degrees" >=%s and "degrees" < 360
                                OR "degrees" >0 and "degrees"  <=%s'''

    logging.debug((carPosition, osmId, previousOsmId, carPosition, previousOsmId, osmId, lowerRange, higherRange))
    if lowerRange > higherRange:
        logging.debug("Query " + osmLinesQuery.osmNextIntersection+azimuthFilterModified)
        cursor.execute(osmLinesQuery.osmNextIntersection+azimuthFilterModified,(carPosition,osmId,previousOsmId,carPosition,previousOsmId,osmId,lowerRange,higherRange))
    else:
        logging.debug("Query " + osmLinesQuery.osmNextIntersection + azimuthFilter)
        cursor.execute(osmLinesQuery.osmNextIntersection+azimuthFilter,(carPosition,osmId,previousOsmId,carPosition,previousOsmId,osmId,lowerRange,higherRange))
    row = cursor.fetchone()
    while row is not None:
        logging.debug(row)
        availableIntersections = MatchingRoads(None, row[0], row[1], row[2])
        listOfAllIntersections.append(availableIntersections)
        row = cursor.fetchone()
    return listOfAllIntersections

def getLineDetails(osmId,pointOnLine):
    logging.debug('Get Line Details')
    cursor.execute(osmLinesQuery.osmLineQuery,(osmId,))
    row = cursor.fetchone()
    logging.debug(row)
    objectLines = OsmLines(row[0],row[1],row[2],row[3])
    logging.debug(objectLines.way)
    logging.debug(objectLines.azimuthBand)
    return objectLines
########################################################################################################################
def validateCarDirectionAndRoadDirectionDelta(roadLinesObj,carAzimuth,matchedIntersectingPoint):
    logging.debug('CarAzimuth ' + str(carAzimuth))
    logging.debug("matched point " + str(matchedIntersectingPoint))
    carDirection = getNSEWQuadrant(carAzimuth)
    logging.debug(carDirection)
    lenLines = len(roadLinesObj.way)
    if lenLines > 2:
        index = roadLinesObj.way.index(matchedIntersectingPoint)
        logging.debug("index = " + str(index))
        if index == (lenLines - 1):
            angle = calculateAzimuthAngle(roadLinesObj.way[index], roadLinesObj.way[index - 1])
            if ( carDirection in getNSEWQuadrantWithDelta(angle)):
                return True
            else:
                logging.debug("Failed , car angle " + str(carAzimuth) + ", road angle " + str(angle))
                return False
        elif index == 0:
            angle = calculateAzimuthAngle(roadLinesObj.way[index], roadLinesObj.way[index + 1])
            if (carDirection in getNSEWQuadrantWithDelta(angle)):
                return True
            else:
                logging.debug("Failed , car angle " + str(carAzimuth) + ", road angle " + str(angle))
                return False
        else:
            listOfGPS = findPosTowardsCarDirection(roadLinesObj.way, carDirection, matchedIntersectingPoint)
            if len(listOfGPS) > 1:
                index = listOfGPS.index(matchedIntersectingPoint)
                if index == 0:
                    angle = calculateAzimuthAngle(listOfGPS[0], listOfGPS[1])
                    if carDirection in getNSEWQuadrantWithDelta(angle):
                        return True
                    else:
                        logging.debug("Failed , car angle " + str(carAzimuth) + ", road angle " + str(angle))
                        return False
                elif index == len(listOfGPS) - 1:
                    angle = calculateAzimuthAngle(listOfGPS[index], listOfGPS[index - 1])
                    if carDirection in getNSEWQuadrantWithDelta(angle):
                        return True
                    else:
                        logging.debug("Failed , car angle " + str(carAzimuth) + ", road angle " + str(angle))
                        return False
            else:
                raise MyError('Not Defined')
    elif lenLines == 2:
        index = roadLinesObj.way.index(matchedIntersectingPoint)
        if index == 0:
            angle = calculateAzimuthAngle(matchedIntersectingPoint, roadLinesObj.way[index + 1])
            if (carDirection in getNSEWQuadrantWithDelta(angle)):
                return True
        else:
            return False

    elif lenLines < 2:
        return False

#=======================================================================================================================

def validateCarDirectionAndRoadDirection(roadLinesObj,carAzimuth,matchedIntersectingPoint):
    logging.debug('CarAzimuth '+str(carAzimuth))
    logging.debug("matched point "+str(matchedIntersectingPoint))
    carDirection = getNSEWQuadrant(carAzimuth)
    logging.debug(carDirection)
    lenLines = len(roadLinesObj.way)
    if lenLines > 2:
        index = roadLinesObj.way.index(matchedIntersectingPoint)
        logging.debug("index = "+str(index))
        if index == (lenLines - 1):
            angle = calculateAzimuthAngle(roadLinesObj.way[index],roadLinesObj.way[index-1])
            if (getNSEWQuadrant(angle) == carDirection):
                return True
            else:
                logging.debug("Failed , car angle "+str(carAzimuth) +", road angle "+str(angle))
                return False
        elif index == 0:
            angle = calculateAzimuthAngle(roadLinesObj.way[index], roadLinesObj.way[index + 1])
            if(getNSEWQuadrant(angle) == carDirection):
                return True
            else:
                logging.debug("Failed , car angle " + str(carAzimuth) + ", road angle " + str(angle))
                return False
        else:
            listOfGPS = findPosTowardsCarDirection(roadLinesObj.way,carDirection,matchedIntersectingPoint)
            if len(listOfGPS) > 1:
                index = listOfGPS.index(matchedIntersectingPoint)
                if index == 0:
                    angle = calculateAzimuthAngle(listOfGPS[0],listOfGPS[1])
                    if getNSEWQuadrant(angle) == carDirection:
                        return True
                    else:
                        logging.debug("Failed , car angle " + str(carAzimuth) + ", road angle " + str(angle))
                        return False
                elif index == len(listOfGPS) - 1:
                    angle = calculateAzimuthAngle(listOfGPS[index],listOfGPS[index-1])
                    if getNSEWQuadrant(angle) == carDirection:
                        return True
                    else:
                        logging.debug("Failed , car angle " + str(carAzimuth) + ", road angle " + str(angle))
                        return False
            else:
                raise MyError('Not Defined')
    elif lenLines == 2:
        index = roadLinesObj.way.index(matchedIntersectingPoint)
        if index == 0:
            angle = calculateAzimuthAngle(matchedIntersectingPoint,roadLinesObj.way[index+1])
            if (getNSEWQuadrant(angle) == getNSEWQuadrant(carAzimuth)):
                return True
        else:
            return False

    elif lenLines < 2:
        return False
##############################################################################################################
def filterIntersectionPointsWhichAllowSpecificTurn():
    logging.debug('To Do')

def findTheRoadMatchingAzimuthAngle(carObj,cursor):
    logging.debug('To Do')


def printObjectDetails(objectData):
    if isinstance(objectData, MatchingRoads):
        #return
        logging.debug(objectData.osmId1)
        logging.debug(objectData.matchedPoint)
        logging.debug(objectData.osmId2)
    elif isinstance(objectData, SelectedLineObj):
        return
        logging.debug(objectData.osmLineId)
        logging.debug(objectData.matchedCoOrdinate)
        logging.debug(objectData.previousOsmLineId)
    else:
        logging.debug("$$$$$$$$$$$$$Didnt Match$$$$$$$$$$$$$$$$$$$$$$")
        logging.debug(objectData)
        logging.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

def processObjectDetails(uniqueRoads,objectData):
     uniqueRoads.update({objectData.osmId1+objectData.osmId2:objectData})


def roadConstruction(routeStack,anglesLeft,totalAnglesToCheck):

    prevMatchingPoint = None
    finalRoad = []
    osmIds = 0
    distance = 0.0
    logging.debug('routeStack' + str(routeStack))
    while len(routeStack) is not 0:
        elem = routeStack.pop(routeStack.keys()[-1])
        printObjectDetails(elem)

        if prevMatchingPoint == None:
            prevMatchingPoint = elem.matchedPoint
            continue
        else:
            distance += calculateDistance(prevMatchingPoint,elem.matchedPoint)
            roadDetails = getLineDetails(elem.osmId1,None)
            findAllGpsCoOrdBetweenPoints(roadDetails.way,prevMatchingPoint,elem.matchedPoint,finalRoad,logging)
            prevMatchingPoint = elem.matchedPoint
            osmIds += elem.osmId1
            logging.debug(finalRoad)

    logging.debug("distance "+str(distance))
    persistTravelledLines(finalRoad,osmIds,anglesLeft,totalAnglesToCheck,distance)
    logging.debug(finalRoad)


def persistTravelledLines(travelLines,osmIds,anglesLeft,totalAnglesToCheck,distance):
    roadString = ''.join(str(str(e) + ',') for e in travelLines)
    roadString = 'LINESTRING(' + roadString[:-1] + ')'
    logging.debug(roadString)
    cursor.callproc('userProc_add_travel_lines', (osmIds,anglesLeft,totalAnglesToCheck,distance,roadString))

def clearRoadLines():
    cursor.execute("Truncate Table planet_osm_lines_traveled;")

def createEndOfRoadsAsIntersection():
    raise MyError("Implement")

def addOrSubtractDeltaForAngles():
    raise MyError("Check if +/- 5 to available angles changes the direction helps to handle error")

def processIntersections(intersectionDetails,allAngles,travelledPath):
    logging.debug("Available Angles " + str(allAngles))
    logging.debug("car next angle "+str(allAngles[0]))
    logging.debug("car remaining angle " + str(allAngles[1:]))
    carObj = CarDetails(intersectionDetails[2],allAngles[0],allAngles[1:])
    osmLineOne = OsmLines(intersectionDetails[0],None,None,intersectionDetails[3])
    osmLineTwo = OsmLines(intersectionDetails[1],None,None,intersectionDetails[4])
    dummyMatchingRoadsObj = MatchingRoads(None,None,None,intersectionDetails[2])
    osmLineOneDirection = carDirectionFunction(osmLineOne,allAngles[0], dummyMatchingRoadsObj.matchedPoint)
    osmLineTwoDirection = carDirectionFunction(osmLineTwo, allAngles[0], dummyMatchingRoadsObj.matchedPoint)

    matchedOsmId = 0
    misMatchedOsmId = 0
    if osmLineOneDirection:
        matchedOsmId = osmLineOne.osmId
        misMatchedOsmId = osmLineTwo.osmId
    elif osmLineTwoDirection:
        matchedOsmId = osmLineTwo.osmId
        misMatchedOsmId = osmLineOne.osmId
    else:
        return

    direction, range = getNSEWQuadrantWithRange(carObj.carAzimuthAngle)
    carObj.previousAngleRange = range
    carObj.setCarPosition(dummyMatchingRoadsObj.matchedPoint)
    matchingRoad = MatchingRoads(None,matchedOsmId,misMatchedOsmId,intersectionDetails[2])
    parentNode = IntersectionNodes(None, matchingRoad, carObj)
    findTheNextIntersectionsToTurn(matchingRoad, carObj, parentNode, travelledPath)


def extractDetailsFromLeafNodes(travelledPath):
    printCollection(travelledPath)
    logging.debug("**********************************************")

    for leaf in travelledPath:
        logging.debug("*************" + str(leaf) + "*****************")
        logging.debug(len(leaf.carObject.carNextAzimuthAngle))
        remainingAngles = leaf.carObject.carNextAzimuthAngle
        logging.debug(leaf.carObject.carPosition)
        ordDict = OrderedDict()
        while leaf is not None:
            printObjectDetails(leaf.objectData)
            processObjectDetails(ordDict, leaf.objectData)
            leaf = leaf.parent
        printDictionary(ordDict)
        roadConstruction(ordDict, len(remainingAngles), totalAnglesToCheck)

#-----------------------------------------------------------------------------------------------------------------
carDirectionFunction = validateCarDirectionAndRoadDirectionDelta
#carDirectionFunction = validateCarDirectionAndRoadDirection
carAzimuthDelta = 5
constraintMatchedAngles = 0
constraintDistance = 0 #KM
#-----------------------------------------------------------------------------------------------------------------
if __name__== "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='(%(threadName)-10s) : %(funcName)s : %(message)s',
                        )
    routeStack = []
    conn = psycopg2.connect("dbname=osm user=praveen password=postgres")
    cursor = conn.cursor()
    carTravelAzimuthAngles = [312.937,20.042,110.078,351.85,351]               #TREMONT #299.1937,19.888,290.1937,206.5 /198.944
    totalAnglesToCheck = len(carTravelAzimuthAngles)
    clearRoadLines()
    queue =  Queue.Queue()
    carPosition0 = CarDetails('-71.085776 42.340944',312.631,carTravelAzimuthAngles)  #42.3408746667 , -71.0857226667

    #carPosition0 = None
    queue.put(carPosition0)
    travelledPath = []
    if carPosition0 is not None:
        while not queue.empty():
            carObj = queue.get()
            mappedObject = findTheRoadMatchingCarPosition(carObj)
            parentNode = IntersectionNodes(None,mappedObject,carObj)
            findTheNextIntersectionsToTurn(mappedObject,carObj,parentNode,travelledPath)

        extractDetailsFromLeafNodes(travelledPath)

    else:
        #find all intersections in the present location.
        logging.debug('Finding Approx Route')
        cursor.execute(osmLinesQuery.allIntersectingNodes)
        row = cursor.fetchone()

        while row is not None:

            processIntersections(row,carTravelAzimuthAngles,travelledPath)
            row = cursor.fetchone()
        extractDetailsFromLeafNodes(travelledPath)

    conn.commit()
    cursor.close()
    conn.close()
