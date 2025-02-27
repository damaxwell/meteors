%CEV_filename.m
%Create filename for an CEV file given
%  drv = Network drive (string)
%  date = date to process (datetime)
%  ext = extension (string)
% Example:
% Z:\PokerFlatMeteorRadar\CEVArchive\201903\METEOR01\ME20190301.000000

function fname = CEV_filename(drv, date, ext)

%Create string for year = yyyy
y = string(year(date));

%Create string for month = MM
if strlength(string(month(date)))==1
    m=strcat('0',string(month(date)));
else
    m=string(month(date));
end

%Create string for day = dd
if strlength(string(day(date)))==1
    d=strcat('0',string(day(date)));
else
    d=string(day(date));
end

%Find correct day folder, e.g. day = 1 or 2 => folder 01, day = 3 or 4 => folder 03
dfolder = day(date)+mod(day(date),2)-1;

%Create string for dfolder = dd
if strlength(string(dfolder))==1
    dfolder=strcat('0',string(dfolder));
else
    dfolder=string(dfolder);
end


fname = strcat(drv,'\PokerFlatMeteorRadar\CEVArchive\',y,m,'\METEOR',dfolder,'\ME',y,m,d,'.',ext);

end

