clear all;
close all;


fileCarSpeed = 'E:\Car Navigation\1-2min analysis\CarSpeed2.csv';
carSpeedData = importdata(fileCarSpeed,',',1);
carSpeedDataValues = carSpeedData.data;

secondsSpeed = carSpeedDataValues(:,2);
secondsSpeed = secondsSpeed - 1515079474;
secondsSpeed = secondsSpeed.*10^9;
nanoSecondsSpeed = carSpeedDataValues(:,3);
totalTimeSpeed = secondsSpeed + nanoSecondsSpeed;
totalTimeSpeed = totalTimeSpeed*10^-9;
velocitySpeed = carSpeedDataValues(:,4)+carSpeedDataValues(:,5)+carSpeedDataValues(:,6)+carSpeedDataValues(:,7);
velocitySpeed = velocitySpeed./4;
deltaDistance = carSpeedDataValues(:,11);


distance = trapz(totalTimeSpeed(~isnan(totalTimeSpeed)),velocitySpeed(~isnan(velocitySpeed)));

disp(distance);
%511.1615m true value 160m 
%
