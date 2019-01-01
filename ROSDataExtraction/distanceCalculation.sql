use CarNavigation;

select SUM(((DeltaT*Velocityx)*power(10,-9))) 'Displacementx' from CarImu where RecordTimeSeconds >= 1515079474 and RecordTimeSeconds<=1515079474+60;

select power(10,-9);

select RecordTimeSeconds,RecordTimeNanoSeconds,CONCAT(latitude,',',longitude) from CarGPS where RecordTimeSeconds >= 1515079474+60;

/*42.34072533333333000000-71.08565333333334000000
42.34160533333333400000,-71.08667733333333000000
129.07 meters
7.8km/hr
52.15651246622518m
*/


Select power(4,0.5);

SELECT SUM(sumDist.Displacementxy) from (
Select dist.RecordTimeSeconds,dist.RecordTimeNanoSeconds,power(power(dist.Displacementx,2) + power(dist.Displacementy,2),0.5) 'Displacementxy' from
(select RecordTimeSeconds,RecordTimeNanoSeconds,DeltaT*Velocityx*power(10,-9) 'Displacementx' , DeltaT*Velocityy*power(10,-9) 'Displacementy' 
from CarImu ) dist
where RecordTimeSeconds >= 1515079474 and RecordTimeSeconds<=1515079474+60) sumDist;

select SUM((DeltaT*Velocityx)*power(10,-9)) 'Displacementx',SUM((DeltaT*Velocityy)*power(10,-9)) 'Displacementy' from CarImu where RecordTimeSeconds >= 1515079474 and RecordTimeSeconds<=1515079474+60;

select * from CarBrakeInfoReport;

select SUM((VelocityOverGround * DeltaT*power(10,-9))) 'Distance m'  from CarBrakeInfoReport where RecordTimeSeconds >= 1515079474 and RecordTimeSeconds<=1515079474+60;