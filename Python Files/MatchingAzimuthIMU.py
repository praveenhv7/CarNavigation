import sys
import mysql.connector
import osmLines
import math
from collections import OrderedDict

class IMUGPS():
    def __init__(self,recordTimeSeconds,latitude,longitude,yaw):
        self.recordTimeSeconds = recordTimeSeconds
        self.latitude = latitude
        self.longitude = longitude
        self.yaw = yaw
        self.azimuth = None
        self.distance = None

    def setAzimuth(self,angle):
        self.azimuth = angle

    def setDistance(self,dist):
        self.distance = dist

def sumOfList(list):
    sum = 0
    for elem in list:
        sum+=elem
    return sum

def connectAndFetchData():

    db = mysql.connector.connect(user='development', password='development', host='10.0.0.17', database='carnavigation')
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    query = """
            select gps.RecordTimeSeconds,gps.latitude,gps.longitude,imu.Yaw 
            from carnavigation.cargps gps left join carnavigation.carimupersec imu
            on (gps.RecordTimeSeconds - 1515079473) = imu.RecordTimeSeconds;
            """
    cursor.execute(query)
    recordKeep = []
    for recordTimeSeconds,latitude,longitude,yaw in cursor:
        imugpsObj = IMUGPS(recordTimeSeconds,latitude,longitude,yaw)

        recordKeep.append(imugpsObj)

    cursor.close()
    db.close()

    imugpsObj = None
    prevLatLong = None
    for imugpsObjNew in recordKeep:
        if prevLatLong == None:
            prevLatLong = str(imugpsObjNew.longitude)+' '+str(imugpsObjNew.latitude)
        else:
            gps1 = prevLatLong
            gps2 = str(imugpsObjNew.longitude)+' '+str(imugpsObjNew.latitude)
            angle = osmLines.calculateAzimuthAngle(gps1,gps2)
            distance = osmLines.calculateDistance(gps1,gps2)
            imugpsObjNew.setAzimuth(angle)
            imugpsObjNew.setDistance(distance)
            prevLatLong = gps2

    for imugpsObj in recordKeep:
        if(imugpsObj.yaw is None):
            continue
        print "Time",imugpsObj.recordTimeSeconds," | :latitude, longitude =",imugpsObj.latitude,",",imugpsObj.longitude, " |\t\t\t\t :YAW",(imugpsObj.yaw + 298)%360, " | \tAZIMUTH:",imugpsObj.azimuth," | \tDISTANCE:",imugpsObj.distance

    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")


    timeFivesBreak = OrderedDict()

    i = 1;
    delta = 10
    pickedAngles = [0]
    print(len(recordKeep))

    print(len(recordKeep)-6)
    while(i<len(recordKeep)-6):
        allAlnglesTensBreak = OrderedDict()
        currentAngle = 0
        currentAngle = (recordKeep[i].yaw+298)%360
        currentAngle = int(currentAngle/20)
        key = 20 * currentAngle
        count = allAlnglesTensBreak.get(key)
        allAlnglesTensBreak.update({key:(count+1)})
        i=i+5

    print allAlnglesTensBreak

if __name__=="__main__":
    connectAndFetchData()

