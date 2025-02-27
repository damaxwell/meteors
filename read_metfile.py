import numpy as np
from datetime import datetime

def parse_multi(values_str, basetype, count):
    """Parse a space separated list of identical types"""
    values = values_str.split()
    if len(values) != count:
        raise ValueError(f"Expected {count} values, got {len(values)}")
                
    return np.array([basetype(v) for v in values])

def parse_location(location_str):
    """Parse LAT,LONG"""
    lat_str, lon_str = location_str.split(',')
    return (float(lat_str), float(lon_str))

def parse_joined_datetime(date_str):
    """Parse date string in format 'YYYY/MM/DD_HH:MM:SS'"""
    date_part, time_part = date_str.split('_')
    return parse_datetime(date_part, time_part)

def parse_datetime(date_part, time_part):
    """Parse date "YYYY/MM/DD" and time "HH:MM:SS" pair"""
    year, month, day = map(int, date_part.split('/'))
    time_parts = time_part.split(':')

    hour = int(time_parts[0])
    minute = int(time_parts[1])

    # The seconds part might contain a decimal point
    seconds_parts = time_parts[2].split('.')
    second = int(seconds_parts[0])
    
    # Handle microseconds if present (convert to microseconds - 1/1,000,000th of a second)
    microsecond = 0
    if len(seconds_parts) > 1:
        # Pad to ensure 6 digits and truncate if longer
        microsecond_str = seconds_parts[1].ljust(6, '0')[:6]
        microsecond = int(microsecond_str)
    
    return datetime(year, month, day, hour, minute, second, microsecond)

def read_complex_signal(f, rec_points):
    """Read `rec_points` complex 16 bit integers and return as a complex64 array"""
    # Skip a 4-character marker
    sep = f.read(4)
    if sep != b'****':
        raise ValueError(f"Expected separator '****', found {sep}")
    
    # Read interleaved real/imaginary data
    # The file has x1, y1, x2, y2, x3, y3, ...
    # The reshape command is row major, so we make a 
    #     rec_points x 2 
    # array
    data = np.fromfile(f, dtype='<i2', count=2*rec_points).reshape(rec_points, 2)

    # Now convert the real and imaginary parts efficiently to a complex array
    signal = np.empty(rec_points, dtype=np.complex64)
    signal.real = data[:, 0]
    signal.imag = data[:, 1]    

    return signal

RECORD_FIELDS = [
    ('File', str),
    ('Rge', float),
    ('Ht', float),
    ('Vrad', float),
    ('delVr', float),
    ('Theta', float),
    ('Phi0', float),
    ('Ambig', int),
    ('Delphase', float),
    ('ant pair', int),
    ('IREX', float),
    ('amax', float),
    ('Tau', float),
    ('vmet', float),
    ('snrdb', float)
] 

FIELDS = [
    ('TYPE', int),
    ('SITENAME', str),
    ('LOCATION', parse_location),
    ('TIME_ZONE', float),
    ('FREQUENCY', float),
    ('LO_FREQUENCY', float),
    ('CHANNELS', int),
    ('RANGE', int),
    ('RESOLUTION', int),
    ('GATES', int),
    ('PRF', int),
    ('ANTENNA_COORDS', lambda x: parse_multi(x, float, 10)),
    ('PHASE_OFFSETS', lambda x: parse_multi(x, float, 5)),
    ('INTEGRATIONS', int),
    ('BASETIME', int),
    ('DATE', parse_joined_datetime),
    ('FILE_SPOOL', str),
    ('MET.RGE#', int),
    ('START.POS', int),
    ('PEAK.POS', int),
    ('RECL_PTS', int),
    ('RECORD_LENGTH', float),
    ('NSMOOTH', int),
    ('MINHT', int),
    ('MAXHT', int),
    ('RXLIST', lambda x: parse_multi(x, int, 5)),
    ('RX_GAIN', int),
    ('TIME_ACCURACY', str),
    ('GPS_STATUS', str),  # Parse this more fully in the future.
    ('VEL_ERR_LIM', float),
    ('SN_ACCEPT_RATIO', float),
    ('T_DECAY_MAX', float),
    ('PLANE_NORMAL', lambda x: parse_multi(x, float, 2)),
    ('PULSE_CODE', str),
    ('MODE', str)
]



class MeteorFile:
    def __init__(self, f):

        self.header = {}

        for field_name, field_type in FIELDS:
            line = f.readline()
            if not line:
                raise ValueError(f"Unexpected EOF while parsing {field_name}")
                
            line = line.decode('utf-8', errors='replace').strip()
            
            # Exepcted field
            field_prefix = field_name + ' '
            if not line.startswith(field_prefix):
                raise ValueError(f"Expected {field_name}, got: {line}")
                
            # Extract value
            value_str = line[len(field_prefix):]
            try:
                self.header[field_name] = field_type(value_str)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid format for {field_name}: {value_str}") from e

        # Skip the "DATA" line
        line = f.readline().decode('utf-8', errors='replace').strip()
        if line != "DATA":
            raise ValueError(f"Expected 'DATA', got: {line}")
    
        # Skip the column headers line
        f.readline()
    
        # Parse AMBIGUITY line
        # Maybe do this more robustly
        ambig_line = f.readline().decode('utf-8', errors='replace').strip()
        if not ambig_line.startswith("AMBIGUITY = "):
            raise ValueError(f"Expected 'AMBIGUITY = ', got: {ambig_line}")
    
        self.header['AMBIGUITY'] = int(ambig_line[13:].strip())

        values = f.readline().decode('utf-8', errors='replace').strip().split()
        record = {}
        record["date"] = parse_datetime(values[0], values[1]);

        for k, (field_name, field_type) in enumerate(RECORD_FIELDS):
            record[field_name] = field_type(values[k+2])
 
        self.record = record

        # Skip the "CORR12" line
        line = f.readline().decode('utf-8', errors='replace').strip()
        if line != "CORR12":
            raise ValueError(f"Expected 'CORR12', got: {line}")

        self.counts = np.fromfile(f, dtype= '<u4', count=1)
        self.lags = np.fromfile(f, dtype= '<f4', count=1)
        self.tshift = np.fromfile(f, dtype= '<f4', count=1)
        self.amplitude = np.fromfile(f, dtype= '<f4', count=500)
        self.phase = np.fromfile(f, dtype= '<f4', count=500)

        # Skip the linebreak at the end of the binary data
        line = f.readline().decode('utf-8', errors='replace').strip()
        if line != "":
            raise ValueError(f"Expected end of line, got: {line}")
        
        # Skip "DATA"
        line = f.readline().decode('utf-8', errors='replace').strip()
        if line != "DATA":
            raise ValueError(f"Expected 'DATA', got: {line}")

        recl_pts = self.header["RECL_PTS"]

        self.rx1 = read_complex_signal(f, recl_pts)
        self.rx2 = read_complex_signal(f, recl_pts)
        self.rx3 = read_complex_signal(f, recl_pts)
        self.rx4 = read_complex_signal(f, recl_pts)
        self.rx5 = read_complex_signal(f, recl_pts)

        # Consume up to 16 bytes of the remaining file.
        # There should only be a four byte separator remaining: '****'
        sep = f.read(16)
        if sep != b'****':
            raise ValueError(f"Expected separator '****', found {sep}")

    def length(self):
        return self.header["RECL_PTS"]

if __name__ == "__main__":
    import sys
    file = sys.argv[1]
    with open(file, "rb") as f:
        data = MeteorFile(f)
        import matplotlib.pyplot as plt

        n = data.counts[0]

        # # Adjust spacing between subplots and around the figure
        # plt.subplots_adjust(
        #     top=0.92,      # Add more space at the top for titles
        #     bottom=0.15,   # Add more space at the bottom for x-axis labels
        #     hspace=0.3     # Increase the height space between subplots
        # )

        amp =  np.abs(data.rx1)
        arg =  np.angle(data.rx1)

        plt.subplot(2,1,1)
        plt.plot(amp)
        # plt.plot(data.amplitude[:n])
        plt.title("Amplitude")
        plt.xlabel("Sample number")
        plt.subplot(2,1,2)
        plt.title("Phase")
        plt.plot(arg)
        # plt.plot(data.phase[:n])
        plt.xlabel("Sample number")
        plt.ylabel("Angle (deg)")
        plt.tight_layout()
        plt.show()
