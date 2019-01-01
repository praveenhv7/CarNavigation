import sys
import psycopg2
import sets
from math import sin, cos, sqrt, atan2, radians,degrees
from decimal import *
from collections import OrderedDict

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
    print listOfAngles
    return min(listOfAngles), max(listOfAngles)


def calculateDeltaBetweenAngles(anglex, angleY):
    maxAngle = max(anglex,angleY)
    minAngle = min(anglex,angleY)
    delta = None
    if maxAngle >= 270.00 and maxAngle < 360 and minAngle >=0 and minAngle <= 90:
        delta = 360 - (maxAngle - minAngle)
    else:
        delta = maxAngle - minAngle
    return delta

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

#print calculateAzimuthAngle('-80.4832 41.14636','-80.48251 41.14534')

#print calculateAzimuthAngle('-80.4813146 41.1697744','-80.481438 41.171234')

#print calculateAzimuthAngle('-80.481438 41.171234','-80.4813146 41.1697744')

#print calculateDistance('-80.4827 41.1456','-80.4834514 41.1467036')

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

#directionnsew, range = getNSEWQuadrantWithRange(22.6)
#print directionnsew, range

#print calculateAzimuthAngle('-71.09725 42.3316','-71.09738 42.33132')
#print calculateAzimuthAngle('-71.09974 42.33154', '-71.09951 42.33201')
#print calculateAzimuthAngle('-71.10004 42.33247','-71.1005 42.33266')
#print calculateAzimuthAngle('-71.10066 42.33261','-71.10076 42.33246')
#print calculateAzimuthAngle('-71.09805 42.33194','-71.09842 42.33204')
#print calculateAzimuthAngle('-71.1001 42.33233','-71.10023 42.33211')
#print calculateAzimuthAngle('-71.09828 42.33107','-71.09814 42.33135')
"""
print checkAngleBetweenXY(20.00,350,355)
print checkAngleBetweenXY(350,20.00,355)
print checkAngleBetweenXY(270.00,290,280)


print checkAngleBetweenXY(20.00,350,345)
print checkAngleBetweenXY(350,20.00,345)
print checkAngleBetweenXY(270.00,290,260)


print checkAngleBetweenXY(20.00,50,45)
print checkAngleBetweenXY(190,230,220)
print checkAngleBetweenXY(270.00,359,280)

print checkAngleBetweenXY(290.00,10,0)
print checkAngleBetweenXY(10,290,5)
print checkAngleBetweenXY(270.00,359,0)
"""
'''
print calculateDeltaBetweenAngles(330, 30)

print calculateDeltaBetweenAngles(45, 30)

print calculateDeltaBetweenAngles(45, 90)

print calculateDeltaBetweenAngles(90, 170)

print calculateDeltaBetweenAngles(270, 180)

print calculateDeltaBetweenAngles(271, 180)

print calculateDeltaBetweenAngles(358, 320)


print calculateDeltaBetweenAngles(352, 0)
'''

dict = OrderedDict()
dict.update({2:"praveen"})
dict.update({1:"hi"})
for keys in dict.keys():
    print keys