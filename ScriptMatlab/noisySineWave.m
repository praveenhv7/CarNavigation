clc;    % Clear the command window.
close all;  % Close all figures (except those of imtool.)
clear;  % Erase all existing variables. Or clearvars if you want.
workspace;  % Make sure the workspace panel is showing.
format long g;
format compact;
fontSize = 25;

% Make a noisy sine wave signal
x = 1 : 300;
period = 50;
y = sin(2*pi*x/period);
noiseAmplitude = 0.8;
y = y + noiseAmplitude * rand(size(y));
subplot(2,1,1);
plot(x, y, 'b-', 'LineWidth', 2);
grid on;
title('Noisy Signal', 'FontSize', fontSize);
% Enlarge figure to full screen.
set(gcf, 'Units', 'Normalized', 'OuterPosition', [0 0 1 1]);
% Give a name to the title bar.
set(gcf, 'Name', 'Demo by ImageAnalyst', 'NumberTitle', 'Off') 

% Now smooth with a Savitzky-Golay sliding polynomial filter
windowWidth = 27
polynomialOrder = 3
smoothY = sgolayfilt(y, polynomialOrder, windowWidth);
subplot(2,1,2);
plot(x, smoothY, 'b-', 'LineWidth', 2);
grid on;
title('Smoothed Signal', 'FontSize', fontSize);