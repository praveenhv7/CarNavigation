clear all;
close all;

folder = 'E:\Car Navigation\5sec analysis\';

fileImu = strcat(folder,'carIMU5sec.csv');
imuData = importdata(fileImu,',',1);
imuDataValues = [0 0 0 0 0 0 0 0 0 0 0 0;imuData.data];

fileCarSpeed = strcat(folder,'carVelocity5sec.csv');
carSpeedData = importdata(fileCarSpeed,',',1);
carSpeedDataValues = [0 0 0;carSpeedData.data];

fileBrakeInfo = strcat(folder,'carAccel5sec.csv');
brakeInfoData = importdata(fileBrakeInfo,',',1);
brakeInfoDataValues = [0 0 0;brakeInfoData.data];

accelerationWheel = brakeInfoDataValues(:,3);
accelerationIMU = imuDataValues(:,7);
velocityCar = carSpeedDataValues(:,3);

time = 0:5;

figure
plot(time,accelerationWheel,'Color',[1.0,0.0,0.0])
hold on
plot(time,accelerationIMU,'Color',[0.0,0.0,1.0])
hold on
plot(time,velocityCar,'Color',[0.0,1.0,0.0])
legend('Acceleration Wheel','AccelerationIMU','VelocityCar')
hold off

distanceFromVelocity = trapz(velocityCar);
fprintf("Distance obtained using trapz on velocity %20.24f.\n",distanceFromVelocity);



Fs = 100;
f = 0.2;

[b,a]=butter(2,f/Fs,'low'); 
[d,c]=butter(2,f/Fs,'high');
a=filter(b,a,accelerationWheel);
v=cumtrapz(time,a);
v=filter(d,c,v);
s=trapz(time,v);

fprintf("Distance obtained integrating acceleration using butter :%20.24f.\n",s);