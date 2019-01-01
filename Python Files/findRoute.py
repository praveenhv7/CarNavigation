import sys
import psycopg2
import sets
from math import sin, cos, sqrt, atan2, radians

#Take the GPS co-ordinates and see if it intersects any road if it does i can assume its on that
#road and draw a line for it till the intersection.
#at intersection see if there s turn to be made.

def calculateDistance(gps1,gps2):

    gps2 = gps2[6:-1]
    print 'GPS1 ->',gps1
    print 'GPS1 ->',gps2
    lat1 = float(gps1.split(" ")[1])
    lon1 = float(gps1.split(" ")[0])
    lat2 = float(gps2.split(" ")[1])
    lon2 = float(gps2.split(" ")[0])
    print 'GPS 1 ->',lat1,',',lon1
    print 'GPS 2 ->', lat2, ',', lon2
    # approximate radius of earth in km
    R = 6373.0

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    print("Result:", distance)
    return distance

def getIndividualCoOrd(roadsGPS):

    lenroadsGPS = len(roadsGPS)
    coOrdWays = roadsGPS[11:lenroadsGPS - 1]
    splitCordWays = coOrdWays.split(",")
    return splitCordWays

def findIfGPSFallsNearAnyRoad():
    conn = psycopg2.connect("dbname=osm user=praveen password=postgres")
    cursor = conn.cursor()
    sqlGps = "select ST_AsText(ST_Transform(gpsCordinates,4326)),heading from planet_osm_first_gps_value;"

    #checks if the car gps position falls near any intersection  if it falls we take the related OSM IDS and check the lines
    #to find nearest GPS position and using heading we find the path
    intersectionSQL = """
                        select l1.*,ST_Distance(l1.matchedPoint,gps.gpsCordinates),ST_AsText(ST_Transform(gps.gpsCordinates,4326)),gps.heading 
                        from planet_osm_intersecting_lines l1, planet_osm_first_gps_value gps
                        ORDER BY ST_Distance ASC LIMIT 4;
                      """
    cursor.execute(intersectionSQL)
    row = cursor.fetchone()
    osmId1 = row[1]
    osmId2 = row[2]
    carGpsCoOrd = row[5]
    heading = row[6]

    print findClosestCoOrdFromOSMIDS(carGpsCoOrd,cursor,[osmId1,osmId2],heading)

    conn.commit();
    cursor.close()
    conn.close()

#fetching all co-ordinates from roads and checking if the GPS position is near to a road location
def findClosestCoOrdFromOSMIDS(carGpsCoOrd,cursor,osmIdList,heading):
    print 'Reported GPS poistion from CAR ', carGpsCoOrd
    min = sys.maxint
    closestCoOrd = None
    finalOsmId = None
    selectedWay = None
    for osmId in osmIdList:
        getLines = "select ST_AsText(ST_Transform(way, 4326)) from planet_osm_line where osm_id = %s"
        cursor.execute(getLines, (osmId,))
        row = cursor.fetchone()
        roadsGPS = row[0]
        allCord = getIndividualCoOrd(roadsGPS)
        for coOrd in allCord:
            distance = calculateDistance(coOrd, carGpsCoOrd)
            if distance < min:
                min = distance
                closestCoOrd = coOrd
                finalOsmId = osmId
                selectedWay = allCord

    print roadsGPS
    print 'Closest Co-ordinate', closestCoOrd

    travel_lines = useHeadingToCreatePath('North',selectedWay,closestCoOrd)
    cursor.callproc('userProc_truncate_travel_lines')
    cursor.callproc('userProc_add_travel_lines', (finalOsmId, travel_lines))


    return (finalOsmId,closestCoOrd,min)

def useHeadingToCreatePath(heading,allRoadCoOrd,closestCoOrd):
    firstCoOrd = allRoadCoOrd[0]
    lastCord = allRoadCoOrd[-1]

    lat1 = float(closestCoOrd.split(" ")[1])
    lon1 = float(closestCoOrd.split(" ")[0])

    lat2 = float(firstCoOrd.split(" ")[1])
    lon2 = float(firstCoOrd.split(" ")[0])

    lat3 = float(lastCord.split(" ")[1])
    lon3 = float(lastCord.split(" ")[0])

    DirectionNS = ''
    DirectionEW = ''

    #take all values in roads which have increasing latitude.
    if 'North' in heading: #check which part of list must be considered.
         if (lat2 - lat1)  > 0:
             print 'Take first half, towards first co-ordinate'
             DirectionNS = 'First'
         elif (lat3 - lat1) > 0:
            print 'Take last half, towards last co-ordinate'
            DirectionNS = 'Last'
    if 'South' in heading:
        if(lat2 - lat1) > 0:
            print 'Take last half towards last co-ordinate'
            DirectionNS = 'Last'
        elif(lat3 -lat1 ) > 0:
            print 'Take first half towards first co-ordinate'
            DirectionNS = 'First'
    if 'East' in heading: #east decrease in longitude values
        if(lon1 - lon2) >0:
            print 'take first half, towards first co-ordinate'
            DirectionEW = 'First'
        elif(lon1 -lon3) > 0:
            print 'take second half, towards last co-ordinate'
            DirectionEW = 'Last'
    if 'West' in heading: #west increase in longitude values
        if(lon2 - lon1) > 0:
            print 'take first half towards first co-ordinate'
            DirectionEW = 'First'
        elif(lon3 - lon1 ):
            print 'take second half, towards last co-ordinate'
            DirectionEW = 'Last'

    firstListWays = []
    lastLListWays = []
    temp = firstListWays
    for roadCoOrd in allRoadCoOrd:
        if (roadCoOrd == closestCoOrd):
            temp = lastLListWays
        temp.append(roadCoOrd)

    print 'Direction ',DirectionNS
    print 'First List elements ',firstListWays
    print 'Last List elements ',lastLListWays

    strReportedWay = 'LINESTRING('
    if DirectionNS == 'Last':
        for co_ordElem in lastLListWays:
            strReportedWay = strReportedWay+co_ordElem+','

    return strReportedWay[:-1]+')'



findIfGPSFallsNearAnyRoad()


