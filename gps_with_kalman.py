from gps_kalman_filter import GPSKalmanFilter
from gps_logger import GpsLogger
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
        print(f"Received GPS message: {msg}")
        timestamp = msg.timestamp
        latitude = msg.latitude
        longitude = msg.longitude

        # convert to xy coords
        gps_x, gps_y = self.convert_to_xy(latitude, longitude)

        if self.last_timestamp is not None:
            dt = (timestamp - self.last_timestamp).total_seconds()
            self.last_timestamp = timestamp
            self.kalman_filter.step(gps_x, gps_y, dt)

        print(f"Received GPS message at {timestamp}, current dt: {dt:.2f} s")
        print(f"Raw GPS: ({latitude}, {longitude}) -> (x: {gps_x:.2f} m, y: {gps_y:.2f} m)")
        print(f"Filtered GPS: (x: {self.kalman_filter.x:.2f} m, y: {self.kalman_filter.y:.2f} m)")
        print(f"Velocity: (vx: {self.kalman_filter.x_dot:.2f} m/s, vy: {self.kalman_filter.y_dot:.2f} m/s, speed: {self.kalman_filter.speed:.2f} m/s)")
        print('='*40)

    
    def convert_to_xy(self, latitude: float, longitude: float) -> tuple[float, float]:
        # simple equirectangular approximation for small distances
        R = 6371000  # Earth radius in meters
        x = R * np.radians(longitude)
        y = R * np.radians(latitude)
        return x, y


if __name__ == '__main__':
    gps_kalman = GpsKalman()
    try:
        gps_kalman.start()
        while not gps_kalman.shutdown_event.is_set():
            pass
    except KeyboardInterrupt:
        gps_kalman.stop()
        print('Exiting')