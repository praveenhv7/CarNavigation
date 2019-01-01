clear all;
close all;

folder = 'E:\Car Navigation\1 second analysis\';

fileImu = strcat(folder,'carimu1sec.csv');
imuData = importdata(fileImu,',',1);
imuDataValues = imuData.data;

fileCarSpeed = strcat(folder,'carvel1sec.csv');
carSpeedData = importdata(fileCarSpeed,',',1);
carSpeedDataValues = carSpeedData.data;

fileBrakeInfo = strcat(folder,'caraccel1sec.csv');
brakeInfoData = importdata(fileBrakeInfo,',',1);
brakeInfoDataValues = brakeInfoData.data;

sumVelocity = carSpeedDataValues(:,2)+carSpeedDataValues(:,3)+carSpeedDataValues(:,4)+carSpeedDataValues(:,5);
avgVelocity = sumVelocity./4;

figure
plot(imuDataValues(:,1),imuDataValues(:,2),'Color',[1.0,0.0,0.0])
hold on
plot(carSpeedDataValues(:,1),avgVelocity,'Color',[0.0,1.0,0.0])
hold on
plot(brakeInfoDataValues(:,1),brakeInfoDataValues(:,2),'Color',[0.0,0.0,1.0])
legend('LinearAccelerationX','Velocity Wheel','Wheel Acceleration')
hold off


