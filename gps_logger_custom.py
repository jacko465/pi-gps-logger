import serial
from time import sleep
import re

# for sparkqEE gps module https://web.archive.org/web/20220709043726/http://www.sparqee.com/portfolio/sparqee-gps/
# Connect to raspberry pi UART interface (GPIO14 - TX, GPIO15 - RX)
# need one pin for enable/disable the module (GPIO4) ** either that or just pull pin high to 3.3v

# after much pain I discovered that I could use the pynmea2 library instead!

class GpsLogger:
    def __init__(self):
        self.running = True

    def start(self):
        print("Opening serial port...")
        num_lines = 0
        with serial.Serial('/dev/serial0', baudrate=9600, timeout=1) as ser:
            print("Waiting for GPS data...")
            while self.running:
                line = ser.readline().decode('ascii', errors='replace').strip()
                
                if line:
                    data = None
                    num_lines += 1
                    print(f'packets received: {num_lines}')
                    # parsing position data from packets
                    if line.startswith('$GPGGA'):
                        data = self.parse_GPGGA(line)
                    elif line.startswith('$GPRMC'):
                        data = self.parse_GPRMC(line)
                    elif line.startswith('$GPGLL'):
                        data = self.parse_GPGLL(line)
                    
                    if data:
                        print(line)
                        print(f"packet type: {data.get('packet_type')}    coords: {data.get('lat')}, {data.get('lon')}    altitude: {data.get('altitude')}")

                sleep(0.01)

    def parse_GPRMC(self, data):
        pass

    def parse_GPGLL(self, data):
        pass

    def parse_GPGGA(self, data):
        parts = data.split(',')
        if parts[0] == '$GPGGA':
            try:
                parsed_data = {
                    'packet_type': parts[0],
                    'utc_time': parts[1],
                    'lat_raw': parts[2],
                    'lat_dir': parts[3],
                    'lon_raw': parts[4],
                    'lon_dir': parts[5],
                    'fix_quality': parts[6],  # 0 = invalid, 1 = GPS fix, 2 = DGPS fix
                    'altitude': parts[9],
                    'checksum': parts[14]
                }
                # get decimal latitude and longitude
                parsed_data['lat'] = self.convert_to_decimal(parsed_data['lat_raw'], parsed_data['lat_dir'], 'lat')
                parsed_data['lon'] = self.convert_to_decimal(parsed_data['lon_raw'], parsed_data['lon_dir'], 'lon')

                if self.validate_packet(data):
                    return parsed_data
                else:
                    raise RuntimeError("Invalid checksum in packet data")
            except Exception as e:
                print(f"Error in parse_GPGGA: {e}")
                return None

    def validate_packet(self, nmea_sentence):
        match = re.match(r'^\$(.*)\*(\w{2})$', nmea_sentence.strip())
        if not match:
            return False
        data_part, checksum_str = match.groups()
        checksum_calculated = 0
        for char in data_part:
            checksum_calculated ^= ord(char)
        checksum_calculated_str = f"{checksum_calculated:02X}"
        return checksum_calculated_str.upper() == checksum_str.upper()

    def convert_to_decimal(self, coord, direction, coord_type):
        if not coord or not direction:
            return None  # Return None if coordinate or direction is missing

        # Determine the degrees and minutes
        if coord_type == 'lat':
            degrees = int(coord[:2])
            minutes = float(coord[2:])
        elif coord_type == 'lon':
            degrees = int(coord[:3])
            minutes = float(coord[3:])
        else:
            raise ValueError('Invalid coordinate type specified.')

        # Convert to decimal degrees
        decimal_degrees = degrees + minutes / 60.0

        # Apply negative sign for South and West coordinates
        if direction in ['S', 'W']:
            decimal_degrees *= -1
        elif direction not in ['N', 'E']:
            raise ValueError('Invalid direction indicator.')

        return decimal_degrees

if __name__ == '__main__':
    try:
        gps_logger = GpsLogger()
        gps_logger.start()
    except KeyboardInterrupt:
        gps_logger.running = False