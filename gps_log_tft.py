from gps_logger import GpsLogger
from tft_update_information import TFT_Updater
from shutdown_manager import ShutdownManager
import time

class GpsTftUpdater(TFT_Updater, GpsLogger):
    def __init__(self):
        self.current_timer = time.time()
        self.time_since_update = 0
        self.lat = None
        self.lon = None
        self.altitude = None
        self.gps_fix = False
        TFT_Updater.__init__(self)
        GpsLogger.__init__(self)

    def msg_handler(self, msg):
        # fix_quality = msg.gps_qual
        if msg.latitude or msg.longitude:
            self.gps_fix = True
        if self.gps_fix:
            self.lat = msg.latitude
            self.lon = msg.longitude
            self.altitude = msg.altitude

            self.time_since_update = time.time() - self.current_timer
            self.current_timer = time.time()
            print(msg)
        print(f'lat: {msg.latitude} lon: {msg.longitude}')
        print(round(self.time_since_update, 3))

if __name__ == '__main__':
    with GpsTftUpdater() as gps_tft:
        try:
            print(f'serial port: {gps_tft.serial_port}')
            gps_tft.draw_text('WAITING FOR GPS...', (0, 0), text_size=30)
            gps_tft.update()
            gps_tft.start_thread()
            while not gps_tft.shutdown_event.is_set():
                if gps_tft.gps_fix:
                    gps_text = f'Coords:\n{gps_tft.lat},{gps_tft.lon}\nAltitude: {gps_tft.altitude}'
                    latency_text = f'Msg latency: {round(gps_tft.time_since_update, 3)}'
                    gps_tft.init_image()
                    gps_tft.draw_text(gps_text, (0, 0), text_size=20)
                    gps_tft.draw_text(latency_text, (0, 100), text_size=20)
                gps_tft.update()
                time.sleep(0.1)

        except KeyboardInterrupt:
            # print(f"Exception: {e}")
            gps_tft.stop_thread()
            print('Exiting')
        finally:
            gps_tft.init_image()
            gps_tft.update()

    #TODO: Might have to change the way the packets are being parsed since the signal seems to be noisy.
    # Investigate if it's worth using regex to grab the packets from the noisy data before parsing them