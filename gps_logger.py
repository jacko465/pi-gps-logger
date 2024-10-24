import io
import pynmea2
import serial

class GpsLogger:
    def __init__(self, serial_port='/dev/serial0', baudrate=9600):
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.running = True
        self.debug = False

    def start(self):
        print("Opening serial port...")
        with serial.Serial(self.serial_port, baudrate=self.baudrate, timeout=1) as ser:
            sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser), encoding='ascii')
            print("Waiting for GPS data...")
            while self.running:
                try:
                    line = sio.readline()
                    msg = pynmea2.parse(line)
                    if self.debug:
                        print(repr(msg))
                    print(f"Coords: {msg.latitude}, {msg.longitude}")
                except serial.SerialException as e:
                    print('Device error: {}'.format(e))
                    break
                except pynmea2.ParseError as e:
                    if self.debug:
                        print('Parse error: {}'.format(e))
                    continue
                except Exception as e:
                    if self.debug:
                        print(f'Exception {e}')
                    continue


if __name__ == '__main__':
    try:
        gps_logger = GpsLogger()
        gps_logger.start()
    except KeyboardInterrupt:
        gps_logger.running = False
        print('Exiting')