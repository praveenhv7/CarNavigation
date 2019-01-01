import osmLinesQuery
from osmLines import *
import psycopg2
import sets
import logging
import random
from math import sin, cos, sqrt, atan2, radians, degrees


conn = psycopg2.connect("dbname=osm user=praveen password=postgres")
cursor = conn.cursor()


def insertIntoIntersectionTable(intersectionListData):

    for elem in intersectionListData:
        logging.debug("Inserting "+str(elem))
        cursor.callproc('userProc_add_intersecting_lines', (elem[0],
                                                            elem[1],
                                                            0.0,
                                                            0.0,
                                                            0.0,
                                                            0.0,
                                                            0.0,
                                                            0.0,
                                                            0.0,
                                                            0.0,
                                                            elem[2]))



def createIntersectionForRoadEnds():

    roadEndsDict = {}
    listOfOSMIds = []
    listOfInsertedPoints = []
    listOfIntersectionData = []
    cursor.execute(osmLinesQuery.allOSMIdQuery)

    row = cursor.fetchone()
    while row is not None:
        listOfOSMIds.append(row[0])
        logging.debug(row)
        row = cursor.fetchone()


    cursor.execute(osmLinesQuery.markBothEndOfRoadsAsIntersection)
    row = cursor.fetchone()
    while row is not None:
        logging.debug("details " + str(row))
        randomNum = random.randint(0,9999999)
        newOSMID = long(row[0]) + randomNum
        if newOSMID not in listOfOSMIds:
            newOSMID = newOSMID * -1
        else:
            newOSMID = (newOSMID+random.randint(1000,5000)) * -1
        secondNewOSMID = random.randint(0,row[0])
        secondNewOSMID += long(row[0])
        secondNewOSMID = secondNewOSMID * -1
        logging.debug("osmId:"+str(row[0])+" : firstOsmId :"+str(newOSMID)+" : secondosmId :"+str(secondNewOSMID))
        startPoint = getIndividualCoOrdPoints(row[1])
        endPoint =  getIndividualCoOrdPoints(row[2])



        if(startPoint not in listOfInsertedPoints):
            listOfIntersectionData.append((row[0],newOSMID,startPoint))
            listOfInsertedPoints.append(startPoint)
        if(endPoint not in listOfInsertedPoints):
            listOfIntersectionData.append((row[0], secondNewOSMID,endPoint ))
            listOfInsertedPoints.append(endPoint)

        row = cursor.fetchone()
    logging.debug("Moving to start of road intersection")
    cursor.execute(osmLinesQuery.markStartOfRoadAsIntersection)
    row = cursor.fetchone()
    while(row is not None):
        startOsmId = ( random.randint(500,1000)+row[0] )*-1
        startPoint = getIndividualCoOrdPoints(row[1])
        if(startPoint not in listOfInsertedPoints):
            listOfIntersectionData.append((row[0],startOsmId,startPoint))
            listOfInsertedPoints.append(startPoint)
        row = cursor.fetchone()

    logging.debug("Moving to end of road intersection")

    cursor.execute(osmLinesQuery.markEndOfRoadAsIntersection)
    row = cursor.fetchone()
    while(row is not None):
        endOsmId =  ( random.randint(500,1000)+row[0] )*-1
        endPoint = getIndividualCoOrdPoints(row[1])
        if(endPoint not in listOfInsertedPoints):
            listOfIntersectionData.append((row[0],endOsmId,endPoint))
            listOfInsertedPoints.append(endPoint)
        row = cursor.fetchone()

    #for elem in listOfIntersectionData:
    #    logging.debug(elem)
    insertIntoIntersectionTable(listOfIntersectionData)






if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='(%(threadName)-10s) : %(funcName)s : %(message)s',
                        )
    createIntersectionForRoadEnds()

    conn.commit()
    cursor.close()
    conn.close()