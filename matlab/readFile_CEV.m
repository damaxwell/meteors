%readFile_CEV(fname)
%
%Reads the CEV file specified by fname into the structure cev
%Returns the structure cev
%
%See below definition for cev structure
%
%?What get's returned if file does not exist?

function cev = readFile_CEV(fname)

fid = fopen(fname);

% READER HEADER

if (fid==-1) %File does not exist, default data
    fprintf('No data for %s\n',fname);

    %Header default values
    cev.type = 2;
    cev.sitename = 'pokerflat';
    cev.lat = 65.1;
    cev.long = -147.5;
    cev.timeZone = -9;
    cev.freq = 32.550; %MHz
    cev.LOFreq = 21.850; %MHz
    cev.channels = 10;
    cev.range = 0;
    cev.resolution = 1.5; %km
    cev.gates = 149;
    cev.PRF = 625;
    cev.antCoords = [23.14 0.00 18.36 180.00 22.91 90.00 18.64 270.00 0.00 0.00];
    cev.phaseOffset = [0.00 -12.60 -15.50 -13.80 -12.80];
    cev.integration = 1;
    cev.basetime = 0; %what is basetime?
    cev.datetime = 0;
    cev.fileSpool = 'local0/Results';
    cev.metRgeN = -1;
    cev.startPos = 0;
    cev.peakPos = 0;
    cev.reclPts = 0;
    cev.recordLength = 4.0000;
    cev.Nsmooth = 5;
    cev.minHt = 70;
    cev.maxHt = 110;
    cev.rxList = [1 1 1 1 1];
    cev.rxGain = 75;
    cev.timeAccuracy = 'HIGH';
    cev.GPSStatus = {'LOCK' 65.126091 'N' 147.491577 'W'};
    cev.velErrLim = 5.50;
    cev.SNAcceptRatio = 2.00;
    cev.TDecayMax = 2.00;
    cev.planeNormal = [0.00 0.00];
    cev.pulseCode = '1110010';
    cev.mode = 'I';
    
    %Data Record 
    cev.dateTime = datetime(0000,1,1); %Year = 0000 indicates no file
    cev.file = cell(1);
    cev.rge = cell(1);
    cev.height = cell(1);
    cev.Vrad = cell(1);
    cev.delVr = cell(1);
    cev.theta = cell(1);
    cev.phi0 = cell(1);
    cev.ambig = cell(1);
    cev.Delphase = cell(1);
    cev.antPair = cell(1);
    cev.IREX = cell(1);
    cev.amax = cell(1);
    cev.tau = cell(1);
    cev.vmet = cell(1);
    cev.snrdb = cell(1);
    
    %fclose(fid);
    
else %Read real data
    cA = textscan(fgetl(fid),'%s %d');
    cev.type = cA{2};
    
    %Site name 'pokerflat'
    cA = textscan(fgetl(fid),'%s %s');
    cev.sitename = cA{2};
    
    %Site latitude and longitude
    cA = textscan(fgetl(fid),'%s %f,%f');
    cev.lat = cA{2};
    cev.long = cA{3};
    
    %Site timezone offset in hours from UTC
    cA = textscan(fgetl(fid),'%s %f');
    cev.timeZone = cA{2};
    
    %Radar operating frequency (MHz)
    cA = textscan(fgetl(fid),'%s %f');
    cev.freq = cA{2}/1e6;
    
    %Radar LO frequency (MHz)
    cA = textscan(fgetl(fid),'%s %f');
    cev.LOFreq = cA{2}/1e6;
    
    %Number of digital channels included in the data read out to the host
    %computer.
    cA = textscan(fgetl(fid),'%s %d');
    cev.channels = cA{2};
    
    %Range of meteor
    cA = textscan(fgetl(fid),'%s %f');
    cev.range = cA{2}; %(m)
    
    %Distance (m) between adjacent radar range gate samples.  Generally
    %this separation is chosen to match the radar system's resolution for a
    %given transmitter pulse length and post detection filter setting.
    cA = textscan(fgetl(fid),'%s %f');
    cev.resolution = cA{2};
    
    %Number of range gates to be sampled based on the values entered for
    %'Resolution' and 'Interval'
    cA = textscan(fgetl(fid),'%s %d');
    cev.gates = cA{2};
    
    %Radar pulse repetition frequency (Hz)
    cA = textscan(fgetl(fid),'%s %d');
    cev.PRF = cA{2};
    
    %Need to revisit this so that I can easily access coordinate of
    %specific antenna
    %Space-separated list of antenna coordinates expressed as range,
    %bearing pairs with the range in meters and the bearing in degrees from
    %true north.
    cA = textscan(fgetl(fid),'%s %f %f %f %f %f %f %f %f %f %f');
    cev.antCoords = [cA{2} cA{3} cA{4} cA{5} cA{6} cA{7} cA{8} cA{9} cA{10} cA{11}];
    
    % Space-separated list of reciver phase propatation delays in degrees
    % expressed as floats.
    cA = textscan(fgetl(fid),'%s %f %f %f %f %f');
    cev.phaseOffset = [cA{2} cA{3} cA{4} cA{5} cA{6}];
    
    %Number of coherent integrations applied to the acquired data. '1'
    %implies no integration
    cA = textscan(fgetl(fid),'%s %d');
    cev.integration = cA{2};
    
    %Basetime ?
    cA = textscan(fgetl(fid),'%s %f');
    cev.basetime = cA{2};
    
    %Date time yyyy/mm/dd_hr:mm:ss
    cA = textscan(fgetl(fid),'%s %s');
    cev.datetime = cA{2};
    
    %File_spool is location on PFMR computer
    cA = textscan(fgetl(fid),'%s %s');
    cev.fileSpool = cA{2};
    
    %metRgeN ??? Possibly the meteor range number (gate?)
    cA = textscan(fgetl(fid),'%s %d');    
    cev.metRgeN = cA{2};
    
    %startPos
    cA = textscan(fgetl(fid),'%s %f');    
    cev.startPos = cA{2};

    %peakPos
    cA = textscan(fgetl(fid),'%s %d');
    cev.peakPos = cA{2};
    
    %reclPts
    cA = textscan(fgetl(fid),'%s %d');
    cev.reclPts = cA{2};
    
    %Record length of detection (s)
    cA = textscan(fgetl(fid),'%s %f');
    cev.recordLength = cA{2};
    
    %No information NSMOOTH
    cA = textscan(fgetl(fid),'%s %d');
    cev.Nsmooth = cA{2};
    
    %Minimum height to which meteors may be allocated by the analysis
    cA = textscan(fgetl(fid),'%s %d');
    cev.minHt = cA{2};
    
    %Maximum height to which meteors may be allocated by the analysis
    cA = textscan(fgetl(fid),'%s %d');
    cev.maxHt = cA{2};
    
    %Space-separated list of zeros or ones indicating which receiver
    %channels should be used for analysis.  Total number of digits equals
    %the number of receivers used during the acquisistion.
    cA = textscan(fgetl(fid),'%s %d %d %d %d %d');
    cev.rxList = [cA{2} cA{3} cA{4} cA{5} cA{6}];
    
    %Rx gain to use during acquisition
    cA = textscan(fgetl(fid),'%s %d');
    cev.rxGain = cA{2};
    
    %Not sure what this means..... Time_Accuracy High?
    cA = textscan(fgetl(fid),'%s %s');
    cev.timeAccuracy = cA{2};
    
    %Status of GPS, e.g. LOCK 65.12 N 147.49 W 
    cA = textscan(fgetl(fid),'%s %s %f %s %f %s');
    cev.GPSStatus = [cA{2} cA{3} cA{4} cA{5} cA{6}];
    
    %Limit on standard deviation of the radial velocity measurement
    %Analysis rejects data with delVr above this value.
    cA = textscan(fgetl(fid),'%s %f');
    cev.velErrLim = cA{2};
    
    %Limit on SNR measurement
    %Analysis rejects data with snrdb less than this value.
    cA = textscan(fgetl(fid),'%s %f');
    cev.SNAcceptRatio = cA{2};
    
    %Limit on Tau measurement
    %Analysis rejects data with tau greater than this value
    cA = textscan(fgetl(fid),'%s %f');
    cev.TDecayMax = cA{2};
    
    %No information Plane Normal
    cA = textscan(fgetl(fid),'%s %f %f');
    cev.planeNormal = [cA{2} cA{3}];
    
    %Pulse code transmitted
    cA = textscan(fgetl(fid),'%s %s');
    cev.pulseCode = cA{2};
    
    %Analysis mode used by skiycorr.  Possibilities include 'I' for normal
    %5-channel interferometric mode and '7' for seven channel mode
    cA = textscan(fgetl(fid),'%s %s');
    cev.mode = cA{2};
    
    %Throw away "DATA"
    cA = textscan(fgetl(fid),'%s');
    
    %Throw away header labels "Date Time File Rge Ht Vrad delVr Theta Phi0
    %Ambig Delphase ant pair IREX amax Tau vmet snrdb
    cA = textscan(fgetl(fid),'%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s');
    
    %Ambiguity = 00, 01, perhaps this is ambiguity level, but don't know
    %what that means
    cA = textscan(fgetl(fid),'%s %s %d');
    cev.ambiguity = cA{3};
    
    if(cev.ambiguity >0)
        %Actual data without Error
        cA = textscan(fgetl(fid), '%d/%d/%d %d:%d:%f %s %f %f %f %f %f %f %d %f %d %d %f %f %f %f');
        cev.errMsg = '0';
        %Convert cell array to structure
        %Date/time of detection relative to UTC
        cev.dateTime = datetime(cA{1},cA{2},cA{3},cA{4},cA{5},cA{6});
    
        %File name extension used to store the raw data for this detection
        cev.file = cA{7};
    
        %Range of detection in km to one decimal place
        cev.rge = cA{8};
    
        %Corrected height above ground of the detection in km
        cev.height = cA{9};
    
        %Radial drift velocity of the detection in m/s
        cev.Vrad = cA{10};
    
        %Standard deviation of the radial velocity measurement obtained from
        %the 5 antenna pairs in the interferometer.  Note that the analysis
        %rejects data with delVr>5.5m/s so that this represents the limiting
        %value for this field in the cev file.
        cev.delVr = cA{11};
    
        %Zenith angle of the detection in degrees
        cev.theta = cA{12};
    
        %Azimuth angle of the detection in degrees measured anticlockwise from
        %East
        cev.phi0 = cA{13};
    
        %Number of locations this detection could have originated from
        cev.ambig = cA{14};
    
        %Worst phase error between antennas if the measured azimuth and zenith
        %of the detection are correct, measured in degrees
        cev.Delphase = cA{15};
    
        %Antenna pair with the worst phase error
        cev.antPair = cA{16};
    
        %Receive channel used in the analysis for certain single-channel data
        %quality tests.  Always "1" during normal operation.
        cev.IREX = cA{17};
    
        %Peak value of the amplitude of the meteor echo in digitiser units.
        %This may be greater than 32767 if channel saturation has occurred.
        cev.amax = cA{18};
    
        %Decay time of the meteor in seconds.  
        %This is the half-life, not a 1/e time constant.
        cev.tau = cA{19};
    
        %Entrance speed of the meteor in km/s.  
        %Bad values are characterised with "-9.99"
        cev.vmet = cA{20};
    
        %Signal-to-noise ratio for this detection in dB
        cev.snrdb = cA{21};
    else
        %Actual data with Error
        cev.errMsg = fgetl(fid);
        %Convert cell array to structure
        %Date/time of detection relative to UTC
        cev.dateTime = 0;
        cev.file = 0;
        cev.rge = 0;
        cev.height = 0;
        cev.Vrad = 0;
        cev.delVr = 0;
        cev.theta = 0;
        cev.phi0 = 0;
        cev.ambig = 0;
        cev.Delphase = 0;
        cev.antPair = 0;
        cev.IREX = 0;
        cev.amax = 0;
        cev.tau = 0;
        cev.vmet = 0;
        cev.snrdb = 0;
    end
    
    %Read Correlation Data
    %Throw away header labels CORR12
    cA = textscan(fgetl(fid), '%s');
    
    %Read number of valid points (4-byte floating point)
    cA = fread(fid, 1, 'uint32');
    cev.corr12.N = cA;
    
    %Read time (lags) between adjacent data points (4-byte floating point)
    cA = fread(fid,1, 'single=>single');
    cev.corr12.lags = cA;
    
    %Read time shift of first (negative) lag of correlation in seconds
    %(4-byte floating point)
    cA = fread(fid, 1, 'single=>single');
    cev.corr12.tshift = cA;
    
    %Read 500 correlation function amplitudes, not all of which may be
    %valid (4-byte floating point)
    cA = fread(fid, 500, 'single=>single');
    cev.corr12.amp = cA;
    
    %Read 500 correlation function phases, not all of which may be valid
    %(4-byte floating point)
    cA = fread(fid, 500, 'single=>single');
    cev.corr12.ph = cA;
    
    %Read Raw Data Samples
    fgetl(fid);
    fgetl(fid); %Should read 'Data'
    
    fread(fid,[1,4],'char=>char'); % ?
    rx=fread(fid,[2,cev.reclPts],'integer*2');
    cev.raw.rx1 = complex(rx(1,:),rx(2,:));
    
    fread(fid,[1,4],'char=>char');
    rx=fread(fid,[2,cev.reclPts],'integer*2');
    cev.raw.rx2 = complex(rx(1,:),rx(2,:));
    
    fread(fid,[1,4],'char=>char');
    rx=fread(fid,[2,cev.reclPts],'integer*2');
    cev.raw.rx3 = complex(rx(1,:),rx(2,:));
    
    fread(fid,[1,4],'char=>char');
    rx=fread(fid,[2,cev.reclPts],'integer*2');
    cev.raw.rx4 = complex(rx(1,:),rx(2,:));    
    
    fread(fid,[1,4],'char=>char');
    rx=fread(fid,[2,cev.reclPts],'integer*2');
    cev.raw.rx5 = complex(rx(1,:),rx(2,:));
    
    fclose(fid);
end
