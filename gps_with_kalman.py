from gps_kalman_filter import GPSKalmanFilter
from gps_logger import GpsLogger
import datetime
import numpy as np
import threading

class GpsKalman(GpsLogger):
    def __init__(self):
        super().__init__()

        self.kalman_filter = GPSKalmanFilter()
        self.last_timestamp = None

    def start(self):
        print("Starting GPS Kalman Filter")
        self.shutdown_event = threading.Event()
        self.running_thread = threading.Thread(target=self.gps_serial, daemon=True)
        self.running_thread.start()

    def stop(self):
        print("Stopping GPS Kalman Filter")
        self.shutdown_event.set()
        self.running_thread.join()

    def msg_handler(self, msg):
        timestamp = msg.timestamp
        latitude = msg.latitude
        longitude = msg.longitude

        # print(f"Raw GPS: ({latitude}, {longitude}) at {timestamp}")

        # convert to xy coords
        gps_x, gps_y = self.convert_to_xy(latitude, longitude)

        print(f"Converted GPS to (x: {gps_x:.2f} m, y: {gps_y:.2f} m)")

        if self.last_timestamp is not None:
            dt = self.get_dt_from_timestamps(self.last_timestamp, timestamp)
            self.kalman_filter.step(gps_x, gps_y, dt)
            print(f"Received GPS message at {timestamp}, current dt: {dt:.2f} s")
            print(f"Raw GPS: ({latitude}, {longitude}) -> (x: {gps_x:.2f} m, y: {gps_y:.2f} m)")
            print(f"Filtered GPS: (x: {self.kalman_filter.x:.2f} m, y: {self.kalman_filter.y:.2f} m)")
            print(f"Velocity: (vx: {self.kalman_filter.x_dot:.2f} m/s, vy: {self.kalman_filter.y_dot:.2f} m/s, speed: {self.kalman_filter.speed:.2f} m/s)")
            print('='*40)
        else:
            print(f"Received first GPS message at {timestamp}, waiting for next to compute dt")

        self.last_timestamp = timestamp

    def get_dt_from_timestamps(self, t1: datetime.time, t2: datetime.time) -> float:
        s1 = self.seconds_since_midnight(t1)
        s2 = self.seconds_since_midnight(t2)
        dt = s2 - s1

        if dt < 0:
            dt += 24 * 3600  # handle midnight rollover
        
        return dt

    def seconds_since_midnight(self, t: datetime.time) -> float:
        return(
            t.hour * 3600 +
            t.minute * 60 +
            t.second +
            t.microsecond / 1e6
        )
    
    def convert_to_xy(self, latitude: float, longitude: float) -> tuple[float, float]:
        # simple equirectangular approximation for small distances
        R = 6371000  # Earth radius in meters
        x = R * np.radians(longitude)
        y = R * np.radians(latitude)
        return x, y
    
    def convert_to_latlon(self, x: float, y: float) -> tuple[float, float]:
        R = 6371000  # Earth radius in meters
        longitude = np.degrees(x / R)
        latitude = np.degrees(y / R)
        return latitude, longitude


if __name__ == '__main__':
    gps_kalman = GpsKalman()
    try:
        gps_kalman.start()
        while not gps_kalman.shutdown_event.is_set():
            pass
    except KeyboardInterrupt:
        gps_kalman.stop()
        print('Exiting')
    except Exception as e:
        print(f"Exception: {e}")
        gps_kalman.stop()
        print('Exiting')