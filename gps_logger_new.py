import pynmea2
import serial
import io

class GpsSerial:
    def __init__(self):
        self.serial_port = '/dev/serial0'
        self.baudrate = 9600
        self.serial_encoding = 'ascii'
        self.debug = False

        self.serial = None
        self.sio = None

    def open_serial(self):
        print("Opening serial port...")
        self.serial = serial.Serial(self.serial_port, baudrate=self.baudrate, timeout=1)
        self.sio = io.TextIOWrapper(io.BufferedRWPair(self.serial, self.serial), encoding=self.serial_encoding)

    def close_serial(self):
        if self.serial:
            self.serial.close()
            print('serial port closed')

if __name__ == '__main__':
    gps_serial = GpsSerial()
    try:
        gps_serial.open_serial()
        print("Waiting for GPS data...")
        while True:
            try:
                line = gps_serial.sio.readline()
                print(line)
            except serial.SerialException as e:
                print(f'Device error: {e}')
                break
    except Exception as e:
        print(f'Exception: {e}')
    finally:
        gps_serial.close_serial()