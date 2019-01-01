truncate CarBrakeInfoReportPerSec;

truncate CarSpeedPerSec;

truncate CarBrakeInfoReportPerSec2;

truncate CarSpeedPerSec2;

select * from CarBrakeInfoReportPerSec2;

select * from CarSpeedPerSec2;

truncate carimupersec2;

select * from carimupersec2;

select RecordTimeSeconds,CONCAT(latitude,',',longitude,',Boston',',#FFFF00') from cargps;

select RecordTimeSeconds,CONCAT(latitude,',',longitude) from cargps;