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

        Dials:
            sigma_gps: GPS measurement noise (meters)
                - lower values trust GPS more
                - higher values trust GPS less and rely more on the model prediction
            sigma_accel: Acceleration noise (m/s^2)
                - lower values assume smoother motion (less acceleration)
                - higher values allow for more erratic motion (more acceleration)
    """
    def __init__(
        self,
        initial_x: float = 0.0,                   # initial position (meters)
        initial_y: float = 0.0,                   # initial position (meters)
        sigma_gps: float = 5.0,             # GPS measurement noise (meters)
        sigma_accel: float = 2.0,           # Acceleration noise (m/s^2)
        initial_velocity_std: float = 10.0  # Initial velocity uncertainty (m/s)
    ):
        self.initial_x = initial_x
        self.initial_y = initial_y
        self.sigma_gps = sigma_gps
        self.sigma_accel = sigma_accel
        self.initial_velocity_std = initial_velocity_std

        # state vector
        # mu_t = [x, y, x_dot, y_dot]
        self.mu = np.array([
            [initial_x],    # initial x position
            [initial_y],    # initial y position
            [0.0],          # initial x velocity
            [0.0]           # initial y velocity
        ], dtype=float)

        # state coviariance
        self.sigma = np.diag([
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

    def make_A(self, dt: float) -> np.ndarray:
        """
            State transition matrix A for constant velocity model
        """
        return np.array([
            [1.0, 0.0, dt, 0.0],  # x' = x + x_dot * dt
            [0.0, 1.0, 0.0, dt],  # y' = y + y_dot * dt
            [0.0, 0.0, 1.0, 0.0], # x_dot' = x_dot (constant velocity)
            [0.0, 0.0, 0.0, 1.0]  # y_dot' = y_dot (constant velocity)
        ], dtype=float)
    
    def make_R(self, dt: float) -> np.ndarray:
        """
            Process noise covariance
            Models unknown acceleration as random noise
            
            Derived from:
                x_k+1 = x_k + x_dot_k * dt + 1/2 * a_x * dt^2
                y_k+1 = y_k + y_dot_k * dt + 1/2 * a_y * dt^2

                x_dot_k+1 = x_dot_k + a_x * dt
                y_dot_k+1 = y_dot_k + a_y * dt

                Not measuring acceleration (ax, ay) directly, modelling it as zero-mean noise
                with variance sigma_accel^2

                R = G * sigma * G^T where G maps acceleration noise into state space
        """
        sigma_a2 = self.sigma_accel**2

        return sigma_a2 * np.array([
            [dt**4/4, 0.0, dt**3/2, 0.0],  # x position variance
            [0.0, dt**4/4, 0.0, dt**3/2],  # y position variance
            [dt**3/2, 0.0, dt**2, 0.0],    # x velocity variance
            [0.0, dt**3/2, 0.0, dt**2]     # y velocity variance
        ], dtype=float)
    
    def make_Q(self, sigma_gps: float) -> np.ndarray:
        """
            Measurement noise covariance
        """
        if sigma_gps is None:
            sigma_gps = self.sigma_gps
        
        return np.array([
            [sigma_gps**2, 0.0],  # x measurement variance
            [0.0, sigma_gps**2]   # y measurement variance
        ], dtype=float)

    def predict(self, dt: float):
        print("in predict step")
        """
            mu_bar = A * mu
            sigma_bar = A * sigma * A^T + R
        """
        A = self.make_A(dt)
        R = self.make_R(dt)

        self.mu = A @ self.mu
        self.sigma = A @ self.sigma @ A.T + R

    def update(self, gps_x: float, gps_y: float, sigma_gps: float | None = None):
        print("in update step")
        """
            Update/correction step using GPS measurement

            K = sigma_bar * H^T * (H * sigma_bar * H^T + Q)^-1
            mu = mu_bar + K * (z - H * mu_bar)
            sigma = (I - K * H) * sigma_bar
        """
        z = np.array([
            [gps_x],  # GPS x measurement
            [gps_y]   # GPS y measurement
        ], dtype=float)
        
        Q = self.make_Q(sigma_gps)

        innovation = z - self.H @ self.mu
        innovation_covariance = self.H @ self.sigma @ self.H.T + Q

        # K = self.sigma @ self.H.T @ np.linalg.inv(innovation_covariance)
        # Using solve for better numerical stability instead of explicit inverse
        K = self.sigma @ self.H.T @ np.linalg.solve(
            innovation_covariance, 
            np.eye(2)
        )

        self.mu = self.mu + K @ innovation
        self.sigma = (self.I - K @ self.H) @ self.sigma

    def step(self, gps_x: float, gps_y: float, dt: float, sigma_gps: float | None = None):
        """
            Convenience method to perform a full predict-update cycle
        """
        print("in step")
        self.predict(dt)
        self.update(gps_x, gps_y, sigma_gps)
        print("leaving step")

    # properties to access state
    @property
    def x(self) -> float:
        return float(self.mu[0, 0])

    @property
    def y(self) -> float:
        return float(self.mu[1, 0])

    @property
    def x_dot(self) -> float:
        return float(self.mu[2, 0])

    @property
    def y_dot(self) -> float:
        return float(self.mu[3, 0])

    @property
    def speed(self) -> float:
        return np.sqrt(self.x_dot**2 + self.y_dot**2)
    
    @property
    def position(self) -> tuple[float, float]:
        return (self.x, self.y)
    
    @property
    def velocity(self) -> tuple[float, float]:
        return (self.x_dot, self.y_dot)

if __name__ == '__main__':
    # init gps
    # feed gps data into kalman filter
    # print results
    pass