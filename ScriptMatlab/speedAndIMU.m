clear all;
close all;

fileImu = 'E:\Car Navigation\1min analysis\carIMU.csv';
imuData = importdata(fileImu,',',1);
imuDataValues = imuData.data;

fileCarSpeed = 'E:\Car Navigation\1min analysis\CarSpeedModified.csv';
carSpeedData = importdata(fileCarSpeed,',',1);
carSpeedDataValues = carSpeedData.data;

fileBrakeInfo = 'E:\Car Navigation\1min analysis\carBrakeInfo.csv';
brakeInfoData = importdata(fileBrakeInfo,',',1);
brakeInfoDataValues = brakeInfoData.data;



secondsIMU = imuDataValues(:,2);
secondsIMU = secondsIMU - 1515079474;
secondsIMU = secondsIMU.*10^9;
nanoSecondsIMU = imuDataValues(:,3);
totalTimeIMU = secondsIMU + nanoSecondsIMU;
totalTimeIMU = totalTimeIMU.*10^-9;
LinearAccelerationXIMU = imuDataValues(:,11);
LinearAccelerationYIMU = imuDataValues(:,12);
LinearAccelerationZIMU = imuDataValues(:,13);

AccelerationXn	= imuDataValues(:,30);
AccelerationYn	= imuDataValues(:,31);
AccelerationZn	= imuDataValues(:,32);

resultantAcceleration = LinearAccelerationXIMU.^2 + LinearAccelerationYIMU.^2;
resultantAcceleration =  resultantAcceleration.^(1/2);
secondsSpeed = carSpeedDataValues(:,2);
secondsSpeed = secondsSpeed - 1515079474;
secondsSpeed = secondsSpeed.*10^9;
nanoSecondsSpeed = carSpeedDataValues(:,3);
totalTimeSpeed = secondsSpeed + nanoSecondsSpeed;
totalTimeSpeed = totalTimeSpeed*10^-9;
velocitySpeed = carSpeedDataValues(:,4)+carSpeedDataValues(:,5)+carSpeedDataValues(:,6)+carSpeedDataValues(:,7);
velocitySpeed = velocitySpeed./4;
deltaDistance = carSpeedDataValues(:,11);
totalDistance = carSpeedDataValues(:,14);
AccelerationSpeed = carSpeedDataValues(:,15);

secondsBrake = brakeInfoDataValues(:,2);
secondsBrake = secondsBrake - 1515079474;
secondsBrake = secondsBrake.*10^9;
nanoSecondsBrake = brakeInfoDataValues(:,3);
totalTimeBrake = secondsBrake + nanoSecondsBrake;
totalTimeBrake = totalTimeBrake.*10^-9;
accelOverGrndBrake = brakeInfoDataValues(:,7);


%plot IMU Acceleration
figure
plot(totalTimeIMU,LinearAccelerationXIMU,'Color',[1.0,0.0,0.0])
hold on
plot(totalTimeIMU,LinearAccelerationYIMU,'Color',[0.0,1.0,0.0])
hold on
plot(totalTimeIMU,LinearAccelerationZIMU,'Color',[0.0,0.0,1.0])
hold on
plot(totalTimeIMU,resultantAcceleration,'Color',[0.0,1.0,1.0])
legend('LinearAccelerationXIMU','LinearAccelerationYIMU','LinearAccelerationZIMU','ResultantAcceleration')
hold off

figure
plot(totalTimeIMU,AccelerationXn,'Color',[1.0,0.0,0.0])
hold on
plot(totalTimeIMU,AccelerationYn,'Color',[0.0,1.0,0.0])
hold on
plot(totalTimeIMU,AccelerationZn,'Color',[0.0,0.0,1.0])
legend('AccelerationXn','AccelerationYn','AccelerationZn')
hold off
%plot speed 
figure
plot(totalTimeSpeed,velocitySpeed,'-*','Color',[0.5,0.0,0.5])
grid on
legend('velocitySpeed')
hold off
%plot brake report
figure
plot(totalTimeBrake,accelOverGrndBrake,'Color',[1.0,0.0,0.0])
legend('accelOverGrndBrake')
hold off
%  Z = trapz(X,Y) computes the integral of Y with respect to X using
%     the trapezoidal method.  X and Y must be vectors of the same
%     length, or X must be a column vector and Y an array whose first
%     non-singleton dimension is length(X).  trapz operates along this
%     dimension.
distance = trapz(totalTimeSpeed(~isnan(totalTimeSpeed)),velocitySpeed(~isnan(velocitySpeed)));
disp(distance)
%distance = distance * 10^-9;
fprintf("Distance obtained integrating speed:%20.24f.\n",distance);
velocity = trapz(totalTimeBrake,accelOverGrndBrake);
%velocity = velocity * 10^-9;
fprintf("Velocity obtained by integrating acceleration:%20.24f.\n",velocity);

velocityIMU = trapz(totalTimeIMU,LinearAccelerationXIMU);
fprintf("Velocity obtained by integrating IMU data: %20.24f.\n",velocityIMU);

figure
plot(totalTimeSpeed,velocitySpeed,'Color',[0.5,0.0,0.5])
hold on
plot(totalTimeSpeed,totalDistance/200,'Color',[0.4,0.2,0.0])
hold on
plot(totalTimeSpeed,deltaDistance*20,'Color',[0.4,0.2,1.0])
hold on
plot(totalTimeSpeed,AccelerationSpeed/8,'Color',[0.1,0.8,0.2])
hold on
plot(totalTimeBrake,accelOverGrndBrake*8,'Color',[1.0,0.0,0.0])
legend('Velocity','Total Distance','Delta Distance','Acceleration Speed','Acceleration')
hold off


%plot x-IMU with brake acceleration
figure 
plot(totalTimeIMU,LinearAccelerationXIMU,'Color',[1.0,0.0,0.0])
hold on
plot(totalTimeBrake,accelOverGrndBrake,'Color',[0.0,1.0,0.0])
legend('Acceleration IMU','Acceleration Brake Report')
hold off

imuFiltered = sgolayfilt(LinearAccelerationXIMU,3,101);
figure
plot(totalTimeIMU,LinearAccelerationXIMU)
hold on
plot(totalTimeIMU,imuFiltered)
hold off

figure
plot(totalTimeBrake,accelOverGrndBrake)
hold on
plot(totalTimeIMU,imuFiltered)
hold off

Y = fft(LinearAccelerationXIMU(2810:3810));
plot(totalTimeIMU(2810:3810),Y);


filterY = highpass(LinearAccelerationXIMU,600);
plot(totalTimeIMU(2810:3810),filterY);