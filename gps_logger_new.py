import pynmea2
import serial

class GpsSerial:
    def __init__(self):
        self.serial_port = '/dev/serial0'
        self.baudrate = 9600
        self.serial_encoding = 'ascii'
        self.debug = False

        self.serial = None

    def open_serial(self):
        print("Opening serial port...")
        

if __name__ == '__main__':
    pass