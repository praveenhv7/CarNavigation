clear all;
close all;

folder = 'E:\Car Navigation\completeData analysis\';
rows = 320;
fileImu = strcat(folder,'carIMU320secv2.csv');
imuData = importdata(fileImu,',',1);
imuDataValues = [0 0 0 0 0 0 0 0 0 0 0 0;imuData.data];

fileCarSpeed = strcat(folder,'carSpeed320secv2.csv');
carSpeedData = importdata(fileCarSpeed,',',1);
carSpeedDataValues = [0 0 0;carSpeedData.data];

fileBrakeInfo = strcat(folder,'carAccl320secv2.csv');
brakeInfoData = importdata(fileBrakeInfo,',',1);
brakeInfoDataValues = [0 0 0;brakeInfoData.data];

velocityCar = carSpeedDataValues(1:rows,3);

time = 1515079474:1515079474+rows-1;

distanceFromVelocity = trapz(velocityCar);
fprintf("Distance obtained using trapz on velocity %20.24f.\n",distanceFromVelocity);


figure
plot(time,brakeInfoDataValues(1:rows,3).*10)
hold on
plot(time,carSpeedDataValues(1:rows,3))
legend('Acceleration Wheel','Speed Wheel')
hold off

figure
plot(time,brakeInfoDataValues(1:rows,3).*10)
hold on
plot(time,imuDataValues(1:rows,7).*10)
legend('Acceleration Wheel','Acceleration IMU')
hold off