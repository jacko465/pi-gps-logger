import numpy as np

class GPSKalmanFilter:
    """
        A simple Kalman Filter implementation for GPS data.
        
        State vector: [x, y, x_dot, y_dot]
        
        Measurement vector: [x, y]

        A = state transition matrix
        H = measurement matrix
        R = process noise covariance
        Q = measurement noise covariance
        Sigma = state covariance

    """
    def __init__(
        self,
        initial_x: float,
        initial_y: float,
        sigma_gps: float = 5.0,  # GPS measurement noise (meters)
        sigma_accel: float = 2.0,  # Acceleration noise (m/s^2)
        initial_velocity_std: float = 10.0  # Initial velocity uncertainty (m/s)
    ):
        self.initial_x = initial_x
        self.initial_y = initial_y
        self.sigma_gps = sigma_gps
        self.sigma_accel = sigma_accel
        self.initial_velocity_std = initial_velocity_std

        # state vector
        # mu_t = [x, y, x_dot, y_dot]
        self.mu_t = np.array([
            [initial_x],    # initial x position
            [initial_y],    # initial y position
            [0.0],          # initial x velocity
            [0.0]           # initial y velocity
        ], dtype=float)

        # state coviariance
        self.sigma_t = np.diag([
            sigma_gps**2,  # position x variance
            sigma_gps**2,  # position y variance
            initial_velocity_std**2,  # velocity x variance
            initial_velocity_std**2   # velocity y variance
        ]).astype(float)

        # H: GPS observes x and y only
        self.H = np.array([
            [1.0, 0.0, 0.0, 0.0],  # x measurement
            [0.0, 1.0, 0.0, 0.0]   # y measurement
        ], dtype=float)

        # I: identity matrix used in covariance update
        self.I = np.eye(4).astype(float)

    def predict(self):
        pass

    def update(self):
        pass



if __name__ == '__main__':
    # init gps
    # feed gps data into kalman filter
    # print results
    pass