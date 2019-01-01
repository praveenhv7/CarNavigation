#find the closest point on a road.
#check cars heading
#see which intersection matches it . i.e. take the azimuth angle between those two intersections
#draw a line from current position to the next intersection
#at intersection check if there s some command available as a stack if so pop it and change the heading

import sys
import psycopg2
import sets
from math import sin, cos, sqrt, atan2, radians,degrees

def getIndividualCoOrdLines(roadsGPS):

    coOrdWays = roadsGPS[11:-1]
    print coOrdWays
    splitCordWays = coOrdWays.split(",")
    return splitCordWays

def getIndividualCoOrdPoints(gpsCord):
    coOrd = gpsCord[6:-1]
    return coOrd

def extractAzimuthOrDecimalValues(decimalValue):
    actualValue = decimalValue[8:-1]
    return float(actualValue)

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

def checkAngleBetweenXY(angleX,angleY,angleCheck):

    maxAngle = max(angleY,angleX)
    minAngle = min(angleY,angleX)

    if angleX > 270.00 or angleY > 270.00:
        if angleX > 0 and angleX < 90:
            #print angleX, ': angleX is above 0 and less than 90 and angle y > 270 ',angleY
            if angleCheck >= 0 and angleCheck <= angleX or angleCheck >= angleY and angleCheck < 360:
                return True
            else:
                return False

        elif angleY >0 and angleY < 90:
            #print angleY, ': angleY is above 0 and less than 90 and angle x > 270 ',angleX
            if angleCheck >=0 and angleCheck <= angleY or angleCheck >= angleX and angleCheck < 360:
                return True
            else:
                return False

        elif angleX >= 270 and angleX <360 and angleY >= 270 and angleY < 360:
            #print 'Entered'
            if angleCheck >= minAngle and angleCheck <= maxAngle:
                return True
            else:
                return False


    else:
        if angleCheck >= minAngle and angleCheck <= maxAngle:
            return True
        else:
            return False



class CarToRoad():

    def __init__(self,osmId,distance,coOrdinate,azimuthStart,azimuthEnd,ways,intersectionCoOrd):
        self.roadOsmID = osmId
        self.distance = distance
        self.coOrdinate = coOrdinate
        self.roadAzimuthStart = azimuthStart
        self.roadAzimuthEnd = azimuthEnd
        self.ways = ways
        self.intersectionCoOrd = intersectionCoOrd

class CarDetails():

    def __init__(self,carGPS,heading):
        self.gpsCoOrdinates = carGPS
        self.heading = 176.00
        #prefill this with valid values. this is a queue to be used after reaching intersection
        self.turns = ['Left']
        self.closestRoadDistance = sys.maxint
        self.closestRoadOsmIds = []

    def toString(self):
        output = "gps co-ordinates "+ self.gpsCoOrdinates +"\n" \
                 "heading direction "+ str(self.heading) +"\n"
        print output


class IntersectionDetails():

    def __init__(self, osmId1, osmId2,
                                azimuthintersectionstartway1,
                                azimuthintersectionendway1,
                                azimuthintersectionstartway2,
                                azimuthintersectionendway2,
                                azimuthbandstartway1,
                                azimuthbandendway1,
                                azimuthbandstartway2,
                                azimuthbandendway2,
                                matchedpoint,
                                distanceToIntersection):
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
        self.distaceToIntersection = distanceToIntersection
        self.carGPSOnRoad = None

    def toString(self):
        objStr = "osmid1 :" + str(self.osmId1) +"\n" \
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
            "distanceToIntersection " + str(self.distaceToIntersection) + "\n" \
            "ways1 "+str(self.ways1) + "\n" \
            "ways2 " + str(self.ways2) + "\n"
        print objStr

    def closestRoad(self,carStateObj):
        #carStateObj = CarDetails()

        minDistance = carStateObj.closestRoadDistance
        azimuthAngle = None
        closestCord = None
        closestOSMId = None
        for roadCoOrd in self.ways1:
            distance = calculateDistance(carStateObj.gpsCoOrdinates,roadCoOrd)
            if distance <= minDistance:
                minDistance = distance
                closestCord = roadCoOrd
                closestOSMId = self.osmId1
                #carStateObj.clearOSMIdList()
                azimuthAngle = (self.azimuthbandstartway1,self.azimuthbandendway1)

        for roadCoOrd in self.ways2:
            distance = calculateDistance(carStateObj.gpsCoOrdinates, roadCoOrd)
            if distance <= minDistance:
                minDistance = distance
                closestCord = roadCoOrd
                closestOSMId = self.osmId2
                #carStateObj.clearOSMIdList()
                azimuthAngle = (self.azimuthbandstartway2,self.azimuthbandendway2)

        carStateObj.closestRoadOsmIds.append((closestOSMId , minDistance ,closestCord , azimuthAngle[0],azimuthAngle[1]))
        carStateObj.closestRoadDistance = minDistance

        #using the car heading calcuate which road matches.
        #car heading is a final azimuth angle. us this to match.

def getNearestLocationOnRoad(interObj, carState,cursor):
    waysSQL = """
                select ST_AsText(ST_Transform(way, 4326)) from planet_osm_line where osm_id = %s;
              """
    cursor.execute(waysSQL, (interObj.osmId1,))
    row = cursor.fetchone()
    interObj.ways1 = getIndividualCoOrdLines(row[0])

    cursor.execute(waysSQL, (interObj.osmId2,))
    row = cursor.fetchone()
    interObj.ways2 = getIndividualCoOrdLines(row[0])

    interObj.closestRoad(carState)



def findIfGPSFallsNearAnyRoad():
    conn = psycopg2.connect("dbname=osm user=praveen password=postgres")
    cursor = conn.cursor()
    intersectionDetailsList = []
    carPosition = None
    #checks if the car gps position falls near any intersection  if it falls we take the related OSM IDS and check the lines
    #to find nearest GPS position and using heading we find the path
    intersectionSQL = """
                            select l1.osm_id1,l1.osm_id2,
							l1.azimuthintersectionstartway1,
							l1.azimuthintersectionendway1,
							l1.azimuthintersectionstartway2,
							l1.azimuthintersectionendway2,
							l1.azimuthbandstartway1,
							l1.azimuthbandendway1,
							l1.azimuthbandstartway2,
							l1.azimuthbandendway2,
							ST_AsText(ST_Transform(l1.matchedpoint,4326)),  
							ST_Distance(ST_Transform(l1.matchedPoint,3857),ST_Transform(gps.gpsCordinates,3857)),ST_AsText(ST_Transform(gps.gpsCordinates,4326)),gps.heading 
                        from planet_osm_intersecting_lines l1, planet_osm_first_gps_position gps
                        ORDER BY ST_Distance ASC LIMIT 4;
                      """
    cursor.execute(intersectionSQL)
    row = cursor.fetchone()
    while row is not None:
        object = IntersectionDetails(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11])
        carPosition = CarDetails(getIndividualCoOrdPoints(row[12]),row[13])
        intersectionDetailsList.append(object)
        row = cursor.fetchone()


    carPosition.toString()

    #Check for the next intersection on the path and load the car  object with all relevant info abt matched road..
    for intersectObj in intersectionDetailsList:
        getNearestLocationOnRoad(intersectObj,carPosition,cursor)


    #(19334350L, 0.07533728149115149, '-80.482293 41.144996', (Decimal('303.0332'), Decimal('282.3763')))
    #consider the case where there are two equal parallel roads we need need to take the on with min azimuth
    #calculate the min and max azimuth angles for the whole set
    minDistSelectedRoad = []
    for closestRoad in carPosition.closestRoadOsmIds:
        print closestRoad
        carAzimuth = carPosition.heading
        roadOsmId = closestRoad[0]
        distance = closestRoad[1]
        nearestCoOrd = closestRoad[2]
        #print str(closestRoad[2])
        startAzimuth = float(closestRoad[3])
        endAzimuth = float(closestRoad[4])
        print startAzimuth ,':',carAzimuth,":",endAzimuth
        if (checkAngleBetweenXY(startAzimuth,endAzimuth,carAzimuth) or
            checkAngleBetweenXY((startAzimuth+180)%360, (endAzimuth+180)%360, carAzimuth) ):
            roadIntersectionDetails = getRoadIntersectionDetails(roadOsmId,intersectionDetailsList)
            roadIntersectionCoOrd = roadIntersectionDetails[2]
            print 'Road Intersection POINT ',roadIntersectionCoOrd , " : nearest Co ordinate on a path connecting intersection ",nearestCoOrd
            azimuthToIntersection = calculateAzimuthAngle(nearestCoOrd,roadIntersectionCoOrd)
            print "azimuth to intersection ",azimuthToIntersection
            print "intersection ->",getNSEWQuadrant(azimuthToIntersection), ' cars ->' ,getNSEWQuadrant(carAzimuth)
            if (getNSEWQuadrant(azimuthToIntersection) == getNSEWQuadrant(carAzimuth)):
                minDistSelectedRoad.append( CarToRoad(roadOsmId,distance,nearestCoOrd,startAzimuth,endAzimuth,roadIntersectionDetails[3],roadIntersectionCoOrd))



    print minDistSelectedRoad
    carDirection = getNSEWQuadrant(carPosition.heading)
    roadTakenMap = {}
    #selected road is nearest matched co-ordinate on road.
    for selectedRoad in minDistSelectedRoad:
        roadTakenMap.update({selectedRoad.roadOsmID:[]})
        for roadCoord in selectedRoad.ways:
            #if getNSEWQuadrant(calculateAzimuthAngle(roadCoord,selectedRoad.coOrdinate)) == carDirection:

            roadCoordlat = float(roadCoord.split(" ")[1])
            roadCoordlon = float(roadCoord.split(" ")[0])
            nearestCoOrdlat = float(selectedRoad.coOrdinate.split(" ")[1])
            nearestCoOrdlon = float(selectedRoad.coOrdinate.split(" ")[0])
            intersectionCoOrdlat = float(selectedRoad.intersectionCoOrd.split(" ")[1])
            intersectionCoOrdlon = float(selectedRoad.intersectionCoOrd.split(" ")[0])

            if carDirection == 'NW':
                #Movement towards North increases latitude
                #Movement towards west decreases longitude
                if (roadCoordlat >= nearestCoOrdlat and roadCoordlon <= nearestCoOrdlon and roadCoordlat <= intersectionCoOrdlat and roadCoordlon >=  intersectionCoOrdlon):
                    roadTakenMap.get(selectedRoad.roadOsmID).append(roadCoord)
            if carDirection == 'N':
                #Movement towards North increases latitude.
                if(roadCoordlat >= nearestCoOrdlat and roadCoordlat <= intersectionCoOrdlat):
                    roadTakenMap.get(selectedRoad.roadOsmID).append(roadCoord)
            if carDirection == 'NE':
                #Movement towards North increases latitude.
                #Movement towards East increases longitude.
                if(roadCoordlat >= nearestCoOrdlat and roadCoordlon >= nearestCoOrdlon and roadCoordlat <= intersectionCoOrdlat and roadCoordlon <= intersectionCoOrdlon):
                    roadTakenMap.get(selectedRoad.roadOsmID).append(roadCoord)
            if carDirection == 'SW':
                #Movement towards south decreases latitude.
                #movement towards west decreases longitude
                if(roadCoordlat <= nearestCoOrdlat and roadCoordlon <= nearestCoOrdlon and roadCoordlat >= intersectionCoOrdlat and roadCoordlon >= intersectionCoOrdlon):
                    roadTakenMap.get(selectedRoad.roadOsmID).append(roadCoord)
            if carDirection == 'S':
                #Movemennt towards south decreases latitude.
                if(roadCoordlat <= nearestCoOrdlat and roadCoordlat >= intersectionCoOrdlat):
                    roadTakenMap.get(selectedRoad.roadOsmID).append(roadCoord)
            if carDirection == 'SE':
                #Movement towards south decreases latitude.
                #Movement towards east increases longitude.
                if(roadCoordlat <= nearestCoOrdlat and roadCoordlon >= nearestCoOrdlon and roadCoordlat >= intersectionCoOrdlat and roadCoordlon <= intersectionCoOrdlon):
                    roadTakenMap.get(selectedRoad.roadOsmID).append(roadCoord)
            if carDirection =='E':
                #Movement towards east increases longitude.
                if(roadCoordlon >= nearestCoOrdlon and roadCoordlon <= intersectionCoOrdlon):
                    roadTakenMap.get(selectedRoad.roadOsmID).append(roadCoord)
            if carDirection == 'W':
                #Movement towards west decreases longitude.
                if(roadCoordlon <= nearestCoOrdlon and roadCoordlon >= intersectionCoOrdlon):
                    roadTakenMap.get(selectedRoad.roadOsmID).append(roadCoord)

    print 'road taken ',roadTakenMap

    #remove truncation and replace with one more backup route table where disregarded route can be removed.
    cursor.callproc('userProc_truncate_travel_lines')

    #TO-DO need a way to use this on each matched road.
    for key in roadTakenMap:
        roadString = ''.join(str(str(e)+',') for e in roadTakenMap.get(key) )
        roadString = 'LINESTRING('+roadString[:-1]+')'
        cursor.callproc('userProc_add_travel_lines', (key, roadString))

    #initial gps was used to find the route to a intersection need to update the car data as the car now


    #is at intersection so theres no need to carry out GPS to road mapping
    # proceed with next road or intersection.
    #road taken has OSM ID for that intersection find the other road to that intersection and


    conn.commit();
    cursor.close()
    conn.close()

def getRoadIntersectionDetails(osmID,intersectionDetailsList):
    for intersectObj in intersectionDetailsList:
        if intersectObj.osmId2 == osmID:
            return (intersectObj.azimuthintersectionstartway2,intersectObj.azimuthintersectionendway2,intersectObj.matchedpoint,intersectObj.ways2)
        elif intersectObj.osmId1 == osmID:
            return (intersectObj.azimuthintersectionstartway1,intersectObj.azimuthintersectionendway1,intersectObj.matchedpoint,intersectObj.ways1)

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



findIfGPSFallsNearAnyRoad()