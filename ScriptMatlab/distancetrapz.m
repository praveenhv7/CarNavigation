clear all;

%vel = [10 5 5 10 5 2 1 0 0 5];
vel = [1 2 2]
time = 0:2;

distance = trapz(vel)
figure
plot(time,vel)