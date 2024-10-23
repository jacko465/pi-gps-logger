import RPi.GPIO as GPIO
import serial
from time import sleep
import re

# for sparkqEE gps module https://web.archive.org/web/20220709043726/http://www.sparqee.com/portfolio/sparqee-gps/
# Connect to raspberry pi UART interface (GPIO14 - TX, GPIO15 - RX)
# need one pin for enable/disable the module (GPIO4) ** either that or just pull pin high to 3.3v


class GpsLogger:
    def __init__(self):
        # self.enable_pin = 4
        self.running = True

        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(self.enable_pin, GPIO.OUT)
        # GPIO.output(self.enable_pin, GPIO.LOW)

    # def __del__(self):
    #     # disable gps module
    #     GPIO.output(self.enable_pin, GPIO.LOW)
    #     GPIO.cleanup()

    def start(self):
        # enable the gps module
        # GPIO.output(self.enable_pin, GPIO.HIGH)

        print("Opening serial port...")
        num_lines = 0
        with serial.Serial('/dev/serial0', baudrate=9600, timeout=1) as ser:
            print("Waiting for GPS data...")
            while self.running:
                line = ser.readline().decode('ascii', errors='replace').strip()
                # if line.startswith('$GPGGA'):
                #     lat, lon, altitude = self.parse_GPGGA(line)
                #     print(f"Coords: {lat}, {lon}    Altitude: {altitude}")
                # if '$GPGGA' in line:
                #     print(line)

                # debug print whole line
                print(line)

                if line:
                    num_lines += 1
                    print(f'num lines received: {num_lines}')
                    try:
                        if '$GPGGA' in line:
                            data = line.split(',')
                            lat, lon, altitude = self.parse_GPGGA(line)
                            print(f'Data: {data}')
                            print(f"Coords: {lat}, {lon}    Altitude: {altitude}")
                    except Exception as e:
                        print(f"Error: {e}")
                        print(f"This is the line: {line}")

                sleep(1)

    def parse_GPGGA(self, data):
        parts = data.split(',')
        if parts[0] == '$GPGGA':
            try:
                lat_raw = parts[2]
                lat_dir = parts[3]
                lon_raw = parts[4]
                lon_dir = parts[5]
                altitude = parts[9]
                lat = self.convert_to_decimal(lat_raw, lat_dir)
                lon = self.convert_to_decimal(lon_raw, lon_dir)
                return lat, lon, altitude
            except IndexError:
                return None, None, None

    def convert_to_decimal(self, value, direction):
        if value == '' or direction == '':
            return None
        degrees = int(value[:2])
        minutes = float(value[2:])
        decimal = degrees + (minutes / 60)
        if direction in ['S', 'W']:
            decimal *= -1
        return decimal

if __name__ == '__main__':
    try:
        gps_logger = GpsLogger()
        gps_logger.start()
    except KeyboardInterrupt:
        gps_logger.running = False