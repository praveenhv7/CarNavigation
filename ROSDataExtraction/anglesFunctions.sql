/*import math

def quaternion_to_euler_angle(w, x, y, z):
	
	t0 = +2.0 * (w * x + y * z)
	t1 = +1.0 - 2.0 * (x * x + y * y)
	X = math.degrees(math.atan2(t0, t1))
	
	t2 = +2.0 * (w * y - z * x)
	t2 = +1.0 if t2 > +1.0 else t2
	t2 = -1.0 if t2 < -1.0 else t2
	Y = math.degrees(math.asin(t2))
	
	t3 = +2.0 * (w * z + x * y)
	t4 = +1.0 - 2.0 * (y * y + z * z)
	Z = math.degrees(math.atan2(t3, t4))
	
	return X, Y, Z
    */
    
    
 DROP FUNCTION IF EXISTS quaternion_to_euler_angle_yaw;

SET DELIMITER $$
create FUNCTION quaternion_to_euler_angle_yaw(
quaternionx DOUBLE,
quaterniony DOUBLE,
quaternionz DOUBLE,
quaternionw DOUBLE
) RETURNS DOUBLE(24,20)
NOT DETERMINISTIC
BEGIN
DECLARE t0 DOUBLE(24,20) DEFAULT 0;
DECLARE t1 DOUBLE(24,20) DEFAULT 0;
DECLARE t2 DOUBLE(24,20) DEFAULT 0;
DECLARE t3 DOUBLE(24,20) DEFAULT 0;
DECLARE t4 DOUBLE(24,20) DEFAULT 0;
DECLARE yaw DOUBLE(24,20) DEFAULT 0;


SET t3 = +2.0 * (quaternionw * quaternionz + quaternionx * quaterniony);
SET	t4 = +1.0 - 2.0 * (quaterniony * quaterniony + quaternionz * quaternionz);
SET	yaw = DEGREES(ATAN2(t3, t4));


RETURN yaw;

END$$
DELIMITER ;
   

USE CarNavigation;

DROP FUNCTION IF EXISTS quaternion_to_euler_angle_pitch;

SET DELIMITER $$
create FUNCTION quaternion_to_euler_angle_pitch(
quaternionx DOUBLE,
quaterniony DOUBLE,
quaternionz DOUBLE,
quaternionw DOUBLE
) RETURNS DOUBLE(24,20)
NOT DETERMINISTIC
BEGIN
DECLARE t0 DOUBLE(24,20) DEFAULT 0;
DECLARE t1 DOUBLE(24,20) DEFAULT 0;
DECLARE t2 DOUBLE(24,20) DEFAULT 0;
DECLARE t3 DOUBLE(24,20) DEFAULT 0;
DECLARE t4 DOUBLE(24,20) DEFAULT 0;
DECLARE pitch DOUBLE(24,20) DEFAULT 0;


SET t2 = +2.0 * (quaternionw * quaterniony - quaternionz * quaternionx);
IF t2 > 1.0
	THEN
    SET t2 = +1.0;
    else
    SET t2 = t2;
END IF;
IF t2 < -1.0 
	THEN
    SET t2 = -1.0;
    ELSE
    SET t2= t2; 
END IF;
SET pitch = DEGREES(ASIN(t2));

RETURN pitch;

END$$
DELIMITER ;

COMMIT;


DROP FUNCTION IF EXISTS quaternion_to_euler_angle_roll;

SET DELIMITER $$
create FUNCTION quaternion_to_euler_angle_roll(
quaternionx DOUBLE,
quaterniony DOUBLE,
quaternionz DOUBLE,
quaternionw DOUBLE
) RETURNS DOUBLE(24,20)
NOT DETERMINISTIC
BEGIN
DECLARE t0 DOUBLE(24,20) DEFAULT 0;
DECLARE t1 DOUBLE(24,20) DEFAULT 0;
DECLARE t2 DOUBLE(24,20) DEFAULT 0;
DECLARE t3 DOUBLE(24,20) DEFAULT 0;
DECLARE t4 DOUBLE(24,20) DEFAULT 0;
DECLARE roll DOUBLE(24,20) DEFAULT 0;


SET t0 = +2.0 * (quaternionw * quaternionx + quaterniony * quaternionz);
SET t1 = +1.0 - 2.0 * (quaternionx * quaternionx + quaterniony * quaterniony);
SET roll = DEGREES(ATAN2(t0,t1));

RETURN roll;

END$$
DELIMITER ;

COMMIT;


CALL quaternion_to_euler_angle(0.70,0.0,0.0,0.70);

USE CarNavigation;

select imu.RecordId,imu.RecordTimeSeconds,imu.RecordTimeNanoSeconds,
quaternion_to_euler_angle_roll(imu.OrientationX,imu.OrientationY,imu.OrientationZ,imu.OrientationW) 'ROLL',
quaternion_to_euler_angle_pitch(imu.OrientationX,imu.OrientationY,imu.OrientationZ,imu.OrientationW) 'PITCH',
quaternion_to_euler_angle_yaw(imu.OrientationX,imu.OrientationY,imu.OrientationZ,imu.OrientationW) 'YAW',
CONCAT(gps.latitude, ', ',gps.longitude) 'lat-long',
imu.LinearAccelerationX,
imu.LinearAccelerationY,
imu.LinearAccelerationZ
from CarNavigation.CarImu imu , CarNavigation.CarGPS gps
where imu.RecordTimeSeconds = gps.RecordTimeSeconds;

and imu.RecordTimeSeconds = 1515079476;

select * from CarNavigation.CarImu imu
WHERE  imu.RecordTimeSeconds = 1515079476;

