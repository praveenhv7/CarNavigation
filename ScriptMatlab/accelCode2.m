clear all;
close all;

filename = 'E:\Car Navigation\ScriptMatlab\IMUCarData.txt';
A = importdata(filename,',',1);
dataA = A.data;
figure
seconds = dataA(:,2);
seconds = seconds - 1515079474;
seconds = seconds.*10^9;
nanoSeconds = dataA(:,3);
totalTime = seconds + nanoSeconds;
totalTime = totalTime * 10^-9;
LinearAccelerationX = dataA(:,11);
LinearAccelerationY = dataA(:,12);
LinearAccelerationZ = dataA(:,13);
plot(totalTime,LinearAccelerationX,'Color',[0.0,1.0,0.0]);
hold on
%plot(totalTime,LinearAccelerationY);
%hold on
%plot(totalTime,LinearAccelerationZ);

Velocityx = dataA(:,18);
%hold on
%plot(totalTime,Velocityx,'Color',[1,0.0,0.0]);
%hold on
Velocityy = dataA(:,19);
Velocityz = dataA(:,20);
DistanceX = dataA(:,21);
%plot(totalTime,DistanceX,'Color',[0,0.0,1.0]);
%legend('AccelerationX','Velocityx','DistanceX')
%hold off
DistanceY = dataA(:,22);
DistanceZ = dataA(:,23);
%figure
Velocityxn = dataA(:,24);
%plot(totalTime,Velocityxn,'Color',[1.0,0.0,0.0]);
%hold on
Velocityyn = dataA(:,25);
Velocityzn = dataA(:,26);
DistanceXn = dataA(:,27);
%plot(totalTime,DistanceXn,'Color',[0.0,1.0,0.0]);
%hold on
DistanceYn = dataA(:,28);
DistanceZn = dataA(:,29);
AccelerationXn = dataA(:,30);
%plot(totalTime,AccelerationXn,'Color',[0.0,0.0,1.0]);
%legend('VelocityX','DistanceX','AccelerationX')
%hold off
AccelerationYn = dataA(:,31);
AccelerationZn = dataA(:,32);
VelocityInstaDist = dataA(:,33);
%plot(totalTime,VelocityInstaDist.*100,'Color',[1.0,0.0,0.0])
VelocityInstaAcc = dataA(:,34);
plot(totalTime,VelocityInstaAcc.*10,'Color',[0.0,0.0,1.0])
legend('AccelerationX','VelocityAccl')
hold off
