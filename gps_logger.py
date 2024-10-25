import io
import pynmea2
import serial
import threading
from time import sleep

class GpsLogger:
    def __init__(self, serial_port='/dev/serial0', baudrate=9600):
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.serial_encoding = 'ascii'
        self.shutdown_event = None  # threading event placeholder
        self.running_thread = None  # daemon thread placeholder
        self.debug = False

    def start_thread(self):
        print("Starting gps_serial thread")
        self.running_thread = threading.Thread(target=self.gps_serial, daemon=True)
        self.running_thread.start()

    def gps_serial(self):
        print("Opening serial port...")
        with serial.Serial(self.serial_port, baudrate=self.baudrate, timeout=1) as ser:
            sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser), encoding=self.serial_encoding)
            print("Waiting for GPS data...")
            self.shutdown_event = threading.Event()
            while not self.shutdown_event.is_set():
                try:
                    line = sio.readline()
                    msg = pynmea2.parse(line)
                    self.msg_handler(msg)
                except serial.SerialException as e:
                    print(f'Device error: {e}')
                    break
                except pynmea2.ParseError as e:
                    if self.debug:
                        print(f'Parse error: {e}')
                    continue
                except Exception as e:
                    if self.debug:
                        print(f'Exception {e}')
                    continue
        print('serial port closed')

    def stop_thread(self):
        print("Stopping gps_serial thread")
        self.shutdown_event.set()
        self.running_thread.join()

    # overload method for subclass implementing actual logging
    def msg_handler(self, msg):
        if self.debug:
            print(repr(msg))
        print(f"Coords: {msg.latitude}, {msg.longitude}     altitude: {msg.altitude}")


if __name__ == '__main__':
    # normal code
    # try:
    #     gps_logger = GpsLogger()
    #     gps_logger.debug = True
    #     gps_logger.gps_serial()
    # except KeyboardInterrupt:
    #     print('Exiting')

    # threading code
    try:
        gps_logger = GpsLogger()
        gps_logger.start_thread()
        gps_logger.running_thread.join()
    except KeyboardInterrupt:
        gps_logger.stop_thread()