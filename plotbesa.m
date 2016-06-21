%userdirectory = uigetdir;%gets user's dir for samples to avg
userdirectory = 'C:\Users\yatri\Desktop\testsamples'; %REMOVE HC LATER!
cd(userdirectory) %chngs directory to the user's specified directory

Files = dir('*.mul*'); %finds all files w/ .mul file extension
Sample = struct; %creates a struct that will hold all sample data
delimiterIn = ' '; %defines what character is b/w each element
headerlinesIn = 2; %defines # of headerlines (which are rows of the file)

for k = 1:length(Files) %go through all files in dir
    AddFile = Files(k).name; %add a file to struct called "Files" holding all files
    A = importdata(Files(k).name,delimiterIn,headerlinesIn); %create temporary struct to transfer data
    Sample(k).data = A.data; %transfer data to the kth sample
    Sample(k).textdata = A.textdata; %transfer textdata to kth sample
    Sample(k).colheaders = A.colheaders; %transfer column headers to kth sample
end

fprintf('\t1: Average & plot F9\n\t2: Average & plot A1\n\t3: Average & plot P9\n\t4: Average & plot Fp1\n\t5: Average & plot F7\n\t6: Average & plot T7\n\t7: Average & plot P7\n\t8: Average & plot O1\n\t9: Average & plot F3\n\t10: Average & plot C3\n\t11: Average & plot P3\n\t12: Average & plot Fpz\n\t13: Average & plot Fz\n\t14: Average & plot Cz\n\t15: Average & plot Pz\n\t16: Average & plot Oz\n\t17: Average & plot F4\n\t18: Average & plot C4\n\t19: Average & plot P4\n\t20: Average & plot Fp2\n\t21: Average & plot F8\n\t22: Average & plot T8\n\t23: Average & plot P8\n\t24: Average & plot O2\n\t25: Average & plot F10\n\t26: Average & plot A2\n\t27: Average & plot P10\n\t28: Average & plot ALL data\n ');
UserChoose = input('What would you like to plot? Please type the number corressponding to your choice:  ', 's')

X = str2double(UserChoose);

if X ~= 28
    for h = 1:length(Sample)-1 %go through all samples
        ColumnSum = Sample(h).data(:,X) + Sample(h+1).data(:,X);
    end
    AvgColumn = ColumnSum/length(Sample);2
    t = size(A.data(:,1));
    t = t(1);
    time = 1:t;
    plot(time, AvgColumn, 'b');
    hold on
else end

if X == 28 
    for j = 1:length(Sample)-1 %go through all samples
        SampleSum = Sample(j).data + Sample(j+1).data;
    end
    Avgall = SampleSum/length(Sample);
    t = size(A.data(:,1));
    t = t(1);
    time = 1:t;
    plot(time,Avgall,'r');
    hold on
else end





%fileA = input('What is the name of the file? :', 's'); %gets filename from
%user input
% fileA = '3005_av-export.mul'; %REMOVE THIS HARDCODE LATER!
% 
% A = importdata(fileA,delimiterIn,headerlinesIn); %A is an array read in 
% coldata = input('What channel would you like to plot?')
% coldataA1 = A.data(:,1); %assigns first column of array A's data
% t = size(A.data(:,1)); %gets size of A to determine time elapsed, returns array
% t = t(1);  %assigns t to time elapsed (first element of t array above)
% time = 1:t; %creates instance of time from 1 second to time elapsed
% %plot (time,coldataA1,'r'); 
% %hold on;
% %fileB = input('What is the name of another file? :', 's');
% fileB = '3009_av-export.mul'; %REMOVE THIS HARDCODE LATER! 
% B = importdata(fileB,delimiterIn,headerlinesIn); 
% C = (A.data + B.data)/2;
% Avgcoldata = C(:,1);
% plot(time,Avgcoldata,'r');
% 
