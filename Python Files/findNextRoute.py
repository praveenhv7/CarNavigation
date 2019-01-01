import sys
import psycopg2
import sets
from math import sin, cos, sqrt, atan2, radians,degrees
import util
import decimal
#***********************************************************************************************************************
#finds the next intersection to be considered if there are no intersections for the current road
#the ends od the road must be considered as intersections.
def findTheNextIntersection(cursor):
    travelDetailQuery = "Select " \
                            "trav.travel_id, "\
                            "inter.osm_id1 ," \
                            "inter.osm_id2," \
                            "inter.azimuthintersectionstartway1," \
                            "inter.azimuthintersectionendway1," \
                            "inter.azimuthintersectionstartway2," \
                            "inter.azimuthintersectionendway2," \
                            "inter.azimuthbandstartway1," \
                            "inter.azimuthbandendway1," \
                            "inter.azimuthbandstartway2," \
                            "inter.azimuthbandendway2," \
                            "ST_AsText(ST_Transform(inter.matchedpoint,4326 )), " \
                            "trav.osm_id "\
                            "from planet_osm_lines_traveled trav, planet_osm_intersecting_lines inter "\
                            "where inter.osm_id1 = trav.osm_id "\
                            "or inter.osm_id2 = trav.osm_id "\
                            "ORDER BY trav.travel_id DESC LIMIT 1; "
    cursor.execute(travelDetailQuery)
    row = cursor.fetchone()
    travelDetails = None
    while row is not None:
        #print row
        travelDetails = util.TravelDetails(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12])
        travelDetails.toString()
        row = cursor.fetchone()



    availableOSMpathId = travelDetails.findNonTravelledOSMId()
    traveledOSMpathId = travelDetails.travelOsmId

    cursor.callproc("get_intersecting_point", (availableOSMpathId, traveledOSMpathId))
    #carPosition = util.getIndividualCoOrdPoints(cursor.fetchone()[0])  # matched point POINT(-80.5119047 41.1564914)
    carPosition = util.getIndividualCoOrdPoints('POINT(-80.5119047 41.1564914)')
    carDetails = util.CarDetails(carPosition,320)
    nextIntersectionQuery = """(select line.osm_id,line.highway,line.name,ST_AsText(ST_Transform(line.way, 4326)),
                                iline.azimuthintersectionstartway1 "azimuthintersectionstartway",
                                iline.azimuthintersectionendway1 "azimuthintersectionendway",
                                iline.azimuthbandstartway1 "azimuthbandstartway",
                                iline.azimuthbandendway1 "azimuthbandendway",
                                ST_AsText(ST_Transform(iline.matchedpoint,4326)) "matchedPoint"
                                from planet_osm_line line,planet_osm_intersecting_lines iline
                                where iline.osm_id1 = line.osm_id
                                and iline.osm_id2 <> %s
                                and line.osm_id = %s)
                                UNION
                                (select line.osm_id,line.highway,line.name,ST_AsText(ST_Transform(line.way, 4326)),
                                iline.azimuthintersectionstartway2 "azimuthintersectionstartway",
                                iline.azimuthintersectionendway2 "azimuthintersectionendway",
                                iline.azimuthbandstartway2 "azimuthbandstartway",
                                iline.azimuthbandendway2 "azimuthbandendway",
                                ST_AsText(ST_Transform(iline.matchedpoint,4326)) "matchedPoint"
                                from planet_osm_line line,planet_osm_intersecting_lines iline
                                where iline.osm_id2 = line.osm_id
                                and iline.osm_id1 <> %s
                                and line.osm_id = %s)
                                LIMIT 4;"""
    cursor.execute(nextIntersectionQuery,(traveledOSMpathId,availableOSMpathId,traveledOSMpathId,availableOSMpathId))
    row = cursor.fetchone()
    nextIntersectionDetailsList = []
    while row is not None:
        print row
        nextIntersection = util.IntersectionToNextIntersection(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9])
        nextIntersectionDetailsList.append(nextIntersection)
        row = cursor.fetchone()

    #check for same intersect as car may have a chance to come back to same point from end of road in case its a dead end or for some other reason..
    if len(nextIntersectionDetailsList) == 0:
        if travelDetails.matchedpoint == carDetails.gpsCoOrdinates:
            print 'Need to find end of road '

        else:
            print 'Car might be taking a U Turn'
            lineSQL = "select line.osm_id,line.highway,line.name,ST_AsText(ST_Transform(line.way, 4326)) " \
                      "from planet_osm_line line where line.osm_id = %s;"
            print lineSQL
            osmLineObjT = None
            cursor.execute(lineSQL, (traveledOSMpathId,))
            row = cursor.fetchone()
            while row is not None:
                osmLineObjT = util.OSMLinesDetails(row[0], row[1], row[2], row[3])
                osmLineObjT.setNextIntersection(travelDetails.matchedpoint,carDetails.gpsCoOrdinates)
                row = cursor.fetchone()
            nextIntersectionDetailsList.append(osmLineObjT)



    #if not intersections are left can be the end of travel use the road end points
    carDirection = util.getNSEWQuadrant(carDetails.heading)
    carFinalPosition = None
    selectedRoad =[]
    if len(nextIntersectionDetailsList) == 0:
        lineObjList = markRoadEndsAsIntersection(travelDetails.travelId,availableOSMpathId,traveledOSMpathId,cursor,carPosition)
        for lines in lineObjList:
            print "Car Heading Towards " + carDirection
            if util.getNSEWQuadrant(lines.angleBeforeCarLoc) == carDirection:
                carToRoad = util.CarToRoad(lines.osmId,0,carDetails.gpsCoOrdinates,lines.angleBeforeCarLoc,lines.angleBeforeCarLoc,lines.waybeforecarLoc,lines.waybeforecarLoc[0])
                selectedRoad.append(carToRoad)
            if util.getNSEWQuadrant(lines.angleAfterCarLoc) == carDirection:
                carToRoad = util.CarToRoad(lines.osmId,0,carDetails.gpsCoOrdinates,lines.angleAfterCarLoc,lines.angleAfterCarLoc,lines.wayAftercarLoc,lines.wayAftercarLoc[-1])
                selectedRoad.append(carToRoad)

    else:
        #TO-DO Select all intersections which matches with the azimuth of the car.
        lineObjList = nextIntersectionDetailsList
        for obj in lineObjList:
            print "Car Heading Towards "+carDirection
            if util.getNSEWQuadrant(obj.azimuthStartIntersect) == carDirection:
                carToRoad = util.CarToRoad(obj.osmId,0,carDetails.gpsCoOrdinates,obj.azimuthStartIntersect,obj.azimuthStartIntersect,obj.wayToIntersection,)

    #check for azimuth car and the calculated values.
    roadTakenMap = {}
    util.addSelectedPOStoTravelMap(selectedRoad, roadTakenMap, carDirection)
    print roadTakenMap



    for key in roadTakenMap:
        roadString = ''.join(str(str(e)+',') for e in roadTakenMap.get(key) )
        roadString = 'LINESTRING('+roadString[:-1]+')'
        cursor.callproc('userProc_add_travel_lines', (key, roadString))



#***********************************************************************************************************************
#take the overall band of the road azimuth angle
#take the start azimuth angle as this helps to determine using cars azimuth
#To-DO check in case of 3-4 intersection.
def markRoadEndsAsIntersection(travelId,availableOSMpathId,traveledOSMpathId,cursor,carPosition):
    print availableOSMpathId
    lineSQL = "select line.osm_id,line.highway,line.name,ST_AsText(ST_Transform(line.way, 4326)) " \
              "from planet_osm_line line where line.osm_id = %s;"
    print lineSQL
    cursor.execute(lineSQL,(availableOSMpathId,))
    row = cursor.fetchone()
    intersectingPoints = []
    osmLineObjNT = None
    while row is not None:
        osmLineObjNT = util.OSMLinesDetails(row[0],row[1],row[2],row[3])
        row = cursor.fetchone()
    osmLineObjNT.extractWayAfterBeforeCarLoc(carPosition)
    osmLineObjT = None
    cursor.execute(lineSQL,(traveledOSMpathId,))
    row = cursor.fetchone()
    while row is not None:
        osmLineObjT = util.OSMLinesDetails(row[0],row[1],row[2],row[3])
        row = cursor.fetchone()
    osmLineObjT.extractWayAfterBeforeCarLoc(carPosition)

    #print carPosition.replace( " ",",")
    azimuthAngle = decimal.Decimal(320.65)
    cursor.callproc("update_car_position",(travelId,long(traveledOSMpathId),carPosition,azimuthAngle))
    return [osmLineObjNT,osmLineObjT]


#***********************************************************************************************************************
def goTowardsCarHeadingIntersection():
    print "To Do"

#***********************************************************************************************************************
def updateCarInformation():
    print "To Do"
#***********************************************************************************************************************
if __name__== "__main__":
    conn = psycopg2.connect("dbname=osm user=praveen password=postgres")
    cursor = conn.cursor()
    findTheNextIntersection(cursor)
    conn.commit()
    cursor.close()
    conn.close()
