clear all;
close all;

folder = 'E:\Car Navigation\completeData analysis\';

fileImu = strcat(folder,'carIMU320sec.csv');
imuData = importdata(fileImu,',',1);
imuDataValues = [0 0 0 0 0 0 0 0 0 0 0 0;imuData.data];

fileCarSpeed = strcat(folder,'carSpeed320sec.csv');
carSpeedData = importdata(fileCarSpeed,',',1);
carSpeedDataValues = [0 0 0;carSpeedData.data];

fileBrakeInfo = strcat(folder,'carAccl320sec.csv');
brakeInfoData = importdata(fileBrakeInfo,',',1);
brakeInfoDataValues = [0 0 0;brakeInfoData.data];


time = 0:10;
acceleration = brakeInfoDataValues(1:11,3);
figure
plot(time,brakeInfoDataValues(1:11,3))
hold on
plot(time,carSpeedDataValues(1:11,3))
legend('Acceleration Wheel','Speed Wheel')
hold off

figure
plot(time,brakeInfoDataValues(1:11,3).*10)
hold on
plot(time,imuDataValues(1:11,7).*10)
legend('Acceleration Wheel','Acceleration IMU')
hold off

velocityObtained = trapz(brakeInfoDataValues(1:11,3))

distanceFromV = trapz(carSpeedDataValues(1:60,3))

