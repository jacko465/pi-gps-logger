import RPi.GPIO as GPIO
import serial
from time import sleep

# for sparkqEE gps module https://web.archive.org/web/20220709043726/http://www.sparqee.com/portfolio/sparqee-gps/
# Connect to raspberry pi UART interface (GPIO14 - TX, GPIO15 - RX)
# need one pin for enable/disable the module (GPIO4)


class GpsLogger:
    def __init__(self):
        self.enable_pin = 4

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.enable_pin, GPIO.OUT)
        GPIO.output(self.enable_pin, GPIO.LOW)

    def __del__(self):
        GPIO.cleanup()

    def start(self):
        # enable the gps module
        GPIO.output(self.enable_pin, GPIO.HIGH)


if __name__ == '__main__':
    pass