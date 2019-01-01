
USE CarNavigation;

DROP TABLE CarNavigation.CarImu;
commit;

select * from CarImu;

CREATE TABLE CarSpeed
(
RecordId int auto_increment,
RecordTimeSeconds int,
RecordTimeNanoSeconds int,

PRIMARY KEY (RecordId),
KEY(RecordTimeSeconds),
Key(RecordTimeSeconds,RecordTimeNanoSeconds)
);

CREATE TABLE CarImu
(
RecordId int auto_increment,
RecordTimeSeconds int,
RecordTimeNanoSeconds int,
OrientationX   DOUBLE(24,20),
OrientationY    DOUBLE(24,20),
OrientationZ    DOUBLE(24,20),
OrientationW    DOUBLE(24,20),
AngularAccelerationX   DOUBLE(24,20),
AngularAccelerationY   DOUBLE(24,20),
AngularAccelerationZ   DOUBLE(24,20),
LinearAccelerationX   DOUBLE(24,20),
LinearAccelerationY   DOUBLE(24,20),
LinearAccelerationZ   DOUBLE(24,20),
Roll DOUBLE(24,20),
Pitch DOUBLE(24,20),
Yaw DOUBLE(24,20),
DeltaT INT,
Velocityx DOUBLE(24,20),
Velocityy DOUBLE(24,20),
Velocityz DOUBLE(24,20),
DistanceX DOUBLE(24,20),
DistanceY DOUBLE(24,20),
DistanceZ DOUBLE(24,20),
Velocityxn DOUBLE(24,20),
Velocityyn DOUBLE(24,20),
Velocityzn DOUBLE(24,20),
DistanceXn DOUBLE(24,20),
DistanceYn DOUBLE(24,20),
DistanceZn DOUBLE(24,20),
AccelerationXn DOUBLE(24,20),
AccelerationYn DOUBLE(24,20),
AccelerationZn DOUBLE(24,20),
VelocityInstaDist DOUBLE(24,20),
VelocityInstaAcc DOUBLE(24,20),
PRIMARY KEY (RecordId),
KEY(RecordTimeSeconds),
Key(RecordTimeSeconds,RecordTimeNanoSeconds)
);

select RecordTimeSeconds,RecordTimeNanoSeconds,
		LinearAccelerationX,DeltaT, Velocityx from CarNavigation.CarImu ;

truncate table CarNavigation.CarImu;

delete from CarNavigation.CarImu;

CREATE TABLE CarImu_V_pithrowyaw
(
RecordId int auto_increment,
RecordTimeSeconds int,
RecordTimeNanoSeconds int,
OrientationX   DOUBLE(24,20),
OrientationY    DOUBLE(24,20),
OrientationZ    DOUBLE(24,20),
OrientationW    DOUBLE(24,20),
AngularAccelerationX   DOUBLE(24,20),
AngularAccelerationY   DOUBLE(24,20),
AngularAccelerationZ   DOUBLE(24,20),
LinearAccelerationX   DOUBLE(24,20),
LinearAccelerationY   DOUBLE(24,20),
LinearAccelerationZ   DOUBLE(24,20),
PRIMARY KEY (RecordId),
KEY(RecordTimeSeconds),
Key(RecordTimeSeconds,RecordTimeNanoSeconds)
);

drop table cargps;

CREATE TABLE CarGPS
(
RecordId int auto_increment,
RecordTimeSeconds int,
RecordTimeNanoSeconds int,
StatusNum smallint,
ServiceNum smallint,
latitude DOUBLE(24,20),
longitude DOUBLE(24,20),
altitude DOUBLE(27,20),
PRIMARY KEY (RecordId),
KEY(RecordTimeSeconds),
Key(RecordTimeSeconds,RecordTimeNanoSeconds)
);

Create TABLE CarSpeed
(
RecordId int auto_increment,
RecordTimeSeconds int,
RecordTimeNanoSeconds int,
velocity_frontLeft DOUBLE(24,20),
velocity_frontRight DOUBLE(24,20),
velocity_backLeft DOUBLE(24,20),
velocity_backRight DOUBLE(24,20),
distance DOUBLE(24,20),
PRIMARY KEY (RecordId),
KEY(RecordTimeSeconds),
Key(RecordTimeSeconds,RecordTimeNanoSeconds)
);

DROP TABLE CarBrakeInfoReport;

truncate table CarBrakeInfoReport;

Create table CarBrakeInfoReport(
RecordId int auto_increment,
RecordTimeSeconds int,
RecordTimeNanoSeconds int,
BrakeTorqueRequest DOUBLE(24,20),
BrakeTorqueActual DOUBLE(24,20),
WheelTorqueActual DOUBLE(24,20),
AccelOverGround DOUBLE(24,20),
VelocityOverGround DOUBLE(24,20),
DistaceOverGround DOUBLE(24,20),
VelocityOverGroundN DOUBLE(24,20),
DistaceOverGroundN DOUBLE(24,20),
DeltaT INT,
stationary Boolean,
PRIMARY KEY (RecordId),
KEY(RecordTimeSeconds),
Key(RecordTimeSeconds,RecordTimeNanoSeconds)
);

select count(*) from CarGPS;

select * from CarGPS;

select count(*) from CarImu;

select RecordId,RecordTimeSeconds,RecordTimeNanoSeconds,OrientationX,OrientationY,OrientationZ,
OrientationW,LinearAccelerationX,LinearAccelerationY,LinearAccelerationZ 
from CarNavigation.CarImu where RecordTimeSeconds >= 1515079473 and RecordTimeSeconds <= 1515079473+5;


select gps.RecordTimeSeconds,CONCAT(gps.latitude, ', ',gps.longitude)
from CarNavigation.CarGPS gps where RecordTimeSeconds >= 1515079791 


select gps.RecordTimeSeconds,CONCAT(gps.latitude, ', ',gps.longitude)
from CarNavigation.CarGPS gps where RecordTimeSeconds >= 1515079473 and RecordTimeSeconds <= 1515079473+20;

select  gps.RecordTimeSeconds,CONCAT(gps.latitude, ', ',gps.longitude)
from CarNavigation.CarGPS gps where RecordTimeSeconds >= 1515079691

select 1515079493-1515079473;

select SIN(45); /*in radians */

quaternion_to_euler_angle()

select RecordId,RecordTimeSeconds,RecordTimeNanoSeconds,quaternion_to_euler_angle(OrientationX,OrientationY,OrientationZ,OrientationW)
from CarNavigation.CarImu where RecordTimeSeconds >= 1515079473 and RecordTimeSeconds <= 1515079473+5;

Create table CarBrakeInfoReportPerSec(
RecordId int auto_increment,
RecordTimeSeconds int,
AccelOverGround DOUBLE(24,20),
PRIMARY KEY (RecordId),
KEY(RecordTimeSeconds)
);
truncate table CarBrakeInfoReportPerSec;
select * from CarBrakeInfoReportPerSec;

create table CarSpeedPerSec(
RecordId int auto_increment,
RecordTimeSeconds int,
velocity_avg DOUBLE(24,20),
PRIMARY KEY (RecordId),
KEY(RecordTimeSeconds)
);

truncate table CarSpeedPerSec;

select * from CarSpeedPerSec;

CREATE TABLE CarImuPerSec
(
RecordId int auto_increment,
RecordTimeSeconds int,
OrientationX   DOUBLE(24,20),
OrientationY    DOUBLE(24,20),
OrientationZ    DOUBLE(24,20),
OrientationW    DOUBLE(24,20),
LinearAccelerationX   DOUBLE(24,20),
LinearAccelerationY   DOUBLE(24,20),
LinearAccelerationZ   DOUBLE(24,20),
Roll DOUBLE(24,20),
Pitch DOUBLE(24,20),
Yaw DOUBLE(24,20),
PRIMARY KEY (RecordId),
KEY(RecordTimeSeconds)
);

truncate table CarImuPerSec;
/*insert into carimupersec (RecordTimeSeconds,OrientationX,OrientationY,OrientationZ,OrientationW,LinearAccelerationX,LinearAccelerationY,LinearAccelerationZ,Roll,Pitch,Yaw) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)*/

select RecordTimeSeconds,roll,pitch,Yaw from carimu  where RecordTimeSeconds <= 1515079474+3;

select * from cargps;

select * from carimupersec;