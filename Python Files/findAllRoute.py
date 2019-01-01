from math import sin, cos, sqrt, atan2, radians, degrees
import sys
import Queue
from osmLines import CarDetails,OsmLines,IntersectionDetails,MatchingRoads,IntersectionNodes,NextRoadForIntersection
from osmLines import calculateAzimuthAngle,getNSEWQuadrant,MyError,SelectedLineObj,findPosTowardsCarDirection
from osmLines import findAllGpsCoOrdBetweenPoints,specialAppend,getNSEWQuadrantWithRange
import logging
import osmLinesQuery
import psycopg2
import copy

#takes the initial position and gets the
#nearest road matching the azimuth.
def findTheRoadMatchingCarPosition(carObj):

    direction, range = getNSEWQuadrantWithRange(carObj.carAzimuthAngle)
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
    return finalIntersectionObj

#the selected near lines intersections are found and the lines are matched based on the
#angles of the azimuth
def findTheNextIntersectionsToTurn(mappedRoadObj,carObj):
    logging.debug('set new position \n find all intersection in this line and send it back ')
    carObj.setCarPosition(mappedRoadObj.nearestPoint)
    carObj.previousPos.append(mappedRoadObj.nearestPoint)
    nonMatchedOsmId = mappedRoadObj.getNonMatchedOsmId()
    #getting the next intersection need to check if the intersections are in same direction as the car's direction.
    cursor.execute(osmLinesQuery.osmNextIntersection,(mappedRoadObj.nearestPointOsmLineId,nonMatchedOsmId,
                                                      nonMatchedOsmId,mappedRoadObj.nearestPointOsmLineId,))
    logging.debug(mappedRoadObj)
    row = cursor.fetchone()
    listOfAllIntersections = []
    while row is not None:
        logging.debug(row)
        availableIntersections = MatchingRoads(None,row[0],row[1],row[2])
        listOfAllIntersections.append(availableIntersections)
        row = cursor.fetchone()

    #return listOfAllIntersections
    newCarObject = copy.deepcopy(carObj)
    matchingRoadStart = MatchingRoads(None,0,mappedRoadObj.nearestPointOsmLineId,None)
    matchingRoadStart.setMatchingPoint(mappedRoadObj.nearestPoint)
    root = IntersectionNodes(None,matchingRoadStart,newCarObject) #root has no data and its the parent

    logging.debug('Starting recursion')
    allTraveledPaths = {}
    startSearchForIntersections(listOfAllIntersections,newCarObject,None,root,allTraveledPaths)
    logging.debug("End of search")
    logging.debug(root.childrens)
#    logging.debug(root.childrens[0].childrens)
    return allTraveledPaths


def printDictionary(allTraveledPaths):
    logging.debug(allTraveledPaths)
    #childNode = allTraveledPaths.get(619015494L)
    #while childNode.parent is not None:
    #    logging.debug(childNode.objectData.osmId1)
    #    childNode = childNode.parent

def startSearchForIntersections(listofAllIntersections,carObj,osmLineId,treeObject,allTraveledPaths):

    if len(listofAllIntersections) == 0 and osmLineId == None:
        return
    elif len(listofAllIntersections) > 0:
        logging.debug("Fist set of Intersections ")

        #make sure osmId1 is the present road and we need to find intersections for osmId2
        for intersection in listofAllIntersections:
            logging.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            newCarObject = copy.deepcopy(carObj)
            nextTree = IntersectionNodes(treeObject,intersection,newCarObject)
            treeObject.addChildrens(nextTree)
            obj = recursiveFindOtherMatches(nextTree,carObj,allTraveledPaths)
            logging.debug('Inserting osmKey :parent:' + str(intersection.osmId2))
            allTraveledPaths.update({intersection.osmId2:obj})
            logging.debug('End of one round ')
            #printDictionary(allTraveledPaths)


    else:
        logging.debug("Next set of Intersections ")
        logging.debug(carObj.carPosition)
        logging.debug(osmLineId.osmLineId)
        logging.debug(osmLineId.previousOsmLineId)
        intersections = getIntersectionRelatedToOSMId(osmLineId.osmLineId,osmLineId.previousOsmLineId)
        if len(intersections) == 0:
            return
        else :
            logging.debug("For each available intersections find next matches")
            for intersection in intersections:
                newCarObject = copy.deepcopy(carObj)
                nextTree = IntersectionNodes(treeObject, intersection,newCarObject)
                treeObject.addChildrens(nextTree)
                obj = recursiveFindOtherMatches(nextTree,carObj,allTraveledPaths)
                logging.debug('Inserting osmKey :leaf:'+str(intersection.osmId2))
                allTraveledPaths.update({intersection.osmId2:obj})
                logging.debug('End of one round ')
                #raise MyError('Implement')





#1. Take an intersection point as a object find the other lines
#   Find the lines that match the car's first azimuth (To - Do)
#   once it matches get the osmID and find for other intersections by passing osmId to the function.
#  this function again returns the next intersections related to that line ...
#
#
def recursiveFindOtherMatches(parentNode,carObj,allTraveledPaths):
    #for the available turns we will find the next available intersections
    if len(carObj.carNextAzimuthAngle) == 0:
        logging.debug("No More Angles left : Returning")
        intersectionDetail = parentNode.objectData
        logging.debug(intersectionDetail)
        logging.debug(intersectionDetail.osmId1)
        logging.debug(intersectionDetail.osmId2)
        logging.debug(intersectionDetail.matchedPoint)
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
        logging.debug(intersectionDetail)
        logging.debug(intersectionDetail.osmId1)
        logging.debug(intersectionDetail.osmId2)
        logging.debug(intersectionDetail.matchedPoint)
        lineDetailsObj = getLineDetails(intersectionDetail.osmId2,intersectionDetail.matchedPoint)
        validDirection = validateCarDirectionAndRoadDirection(lineDetailsObj,angle,intersectionDetail.matchedPoint)
        if validDirection:
            newCarObj.removeFirstAngle()
            logging.debug("remaining angle")
            logging.debug(newCarObj.carNextAzimuthAngle)
            newCarObj.setCarPosition(intersectionDetail.matchedPoint)
            selectedLineObj = SelectedLineObj(lineDetailsObj.osmId,intersectionDetail.matchedPoint,intersectionDetail.osmId1)
            newCarObject = copy.deepcopy(carObj)
            nextNode = IntersectionNodes(parentNode,selectedLineObj,newCarObject)
            parentNode.addChildrens(selectedLineObj)
            startSearchForIntersections([],newCarObj,selectedLineObj,nextNode,allTraveledPaths)
        else:
            logging.debug("Couldn Find valid road")
            #carObj.removeFirstAngle()
            return parentNode
    return parentNode

def getIntersectionRelatedToOSMId(osmId,previousOsmId):
    logging.debug("Get Line Intersection Details for "+str(osmId) +" and " +str(previousOsmId))
    listOfAllIntersections = []
    cursor.execute(osmLinesQuery.osmNextIntersection,(osmId,previousOsmId,previousOsmId,osmId))
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
        #return
        logging.debug(objectData.osmLineId)
        logging.debug(objectData.matchedCoOrdinate)
        logging.debug(objectData.previousOsmLineId)
    else:
        logging.debug("$$$$$$$$$$$$$Didnt Match$$$$$$$$$$$$$$$$$$$$$$")
        logging.debug(objectData)
        logging.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

def roadConstruction(routeStack):

    prevMatchingPoint = None
    finalRoad = []
    osmIds = 0
    logging.debug('routeStack' + str(routeStack))
    while len(routeStack) is not 0:
        elem = routeStack.pop()
        printObjectDetails(elem)

        if isinstance(elem, MatchingRoads):
            if elem.osmId1 == 0:
                prevMatchingPoint = elem.matchedPoint
                continue
            else:
                roadDetails = getLineDetails(elem.osmId1,None)
                findAllGpsCoOrdBetweenPoints(roadDetails.way,prevMatchingPoint,elem.matchedPoint,finalRoad,logging)
                prevMatchingPoint = elem.matchedPoint
                osmIds = elem.osmId2
                logging.debug(finalRoad)

        else:
            continue

    persistTravelledLines(finalRoad,osmIds)
    logging.debug(finalRoad)


def persistTravelledLines(travelLines,osmIds):
    roadString = ''.join(str(str(e) + ',') for e in travelLines)
    roadString = 'LINESTRING(' + roadString[:-1] + ')'
    logging.debug(roadString)
    cursor.callproc('userProc_add_travel_lines', (osmIds, roadString))

def clearRoadLines():
    cursor.execute("Truncate Table planet_osm_lines_traveled;")

def createEndOfRoadsAsIntersection():
    raise MyError("Implement")

def addOrSubtractDeltaForAngles():
    raise MyError("Check if +/- 5 to available angles changes the direction helps to handle error")



if __name__== "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='(%(threadName)-10s) : %(funcName)s : %(message)s',
                        )
    routeStack = []
    conn = psycopg2.connect("dbname=osm user=praveen password=postgres")
    cursor = conn.cursor()

    clearRoadLines()
    queue =  Queue.Queue()
    carPosition0 = CarDetails('-71.09725 42.3316',198.944,[299.1937,19.888]) #299.1937,19.888,290.1937,206.5
    queue.put(carPosition0)
    travelledPath = None
    while not queue.empty():
        carObj = queue.get()
        mappedObject = findTheRoadMatchingCarPosition(carObj)
        travelledPath = findTheNextIntersectionsToTurn(mappedObject,carObj)


    printDictionary(travelledPath)
    logging.debug("**********************************************")

    for leaf in travelledPath.keys():
        logging.debug("*************"+str(leaf)+"*****************")
        object = travelledPath[leaf]
        #logging.debug(object.objectData)
        logging.debug('last line used')
        #printObjectDetails(object.objectData)
        logging.debug(object.objectData)
        logging.debug(object.objectData.osmId1)
        logging.debug(object.objectData.osmId2)
        logging.debug(object.objectData.matchedPoint)
        specialAppend(routeStack,object.objectData)
        parent = object.parent
        while parent is not None:
            logging.debug("+++++++++++++++++")
            #printObjectDetails(parent.objectData)

            specialAppend(routeStack, parent.objectData)
            logging.debug(parent.carObject.carNextAzimuthAngle)
            parent = parent.parent
        logging.debug('+++++++++++++++++++')
        logging.debug(object.carObject.carNextAzimuthAngle)
        logging.debug("*****************end*******************")
        roadConstruction(routeStack)

        #raise MyError('Just first loop')

    conn.commit()
    cursor.close()
    conn.close()
