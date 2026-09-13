import numpy as np
from scipy.linalg import cholesky

class GNSS_INS_UKF:
    """
    Unscented Kalman Filter (UKF) for GNSS and INS (IMU) Sensor Fusion.
    This acts as the core fusion engine during GNSS availability and 
    seamlessly transitions to dead reckoning during GNSS blackout.
    """
    def __init__(self, state_dim=9, meas_dim=3):
        # State: [px, py, pz, vx, vy, vz, roll, pitch, yaw]
        self.n = state_dim
        self.m = meas_dim
        
        # Initial State
        self.x = np.zeros(self.n)
        
        # State Covariance Matrix
        self.P = np.eye(self.n) * 1.0
        
        # Process Noise Covariance (IMU noise)
        self.Q = np.eye(self.n) * 0.01
        
        # Measurement Noise Covariance (GNSS noise)
        self.R = np.eye(self.m) * 2.0
        
        # UKF Parameters
        self.alpha = 1e-3
        self.kappa = 0
        self.beta = 2
        self.lambda_ = self.alpha**2 * (self.n + self.kappa) - self.n
        
        # Weights for means and covariances
        self.Wc = np.full(2 * self.n + 1, 1 / (2 * (self.n + self.lambda_)))
        self.Wm = np.full(2 * self.n + 1, 1 / (2 * (self.n + self.lambda_)))
        self.Wc[0] = self.lambda_ / (self.n + self.lambda_) + (1 - self.alpha**2 + self.beta)
        self.Wm[0] = self.lambda_ / (self.n + self.lambda_)

    def generate_sigma_points(self):
        """ Generates 2n+1 sigma points based on current state and covariance. """
        sigma_points = np.zeros((2 * self.n + 1, self.n))
        sigma_points[0] = self.x
        
        # Cholesky decomposition for matrix square root
        # Add small jitter for numerical stability
        U = cholesky((self.n + self.lambda_) * self.P + np.eye(self.n)*1e-6)
        
        for i in range(self.n):
            sigma_points[i + 1] = self.x + U[i]
            sigma_points[self.n + i + 1] = self.x - U[i]
            
        return sigma_points

    def predict(self, dt, imu_accel, ai_velocity=None):
        """
        Prediction step based on IMU data. 
        If ai_velocity is provided (during GNSS blackout), it replaces/augments the IMU integration.
        """
        sigmas = self.generate_sigma_points()
        
        # State transition function applied to each sigma point
        # A simple kinematic model: p = p + v*dt + 0.5*a*dt^2
        sigmas_pred = np.zeros_like(sigmas)
        for i in range(2 * self.n + 1):
            s = sigmas[i]
            
            # Extract state parts
            pos = s[0:3]
            vel = s[3:6]
            att = s[6:9]
            
            # If we have AI velocity prediction, use it to constrain drift
            if ai_velocity is not None:
                # Update velocity in forward direction based on AI, ignoring pure integration
                vel[0] = ai_velocity * np.cos(att[2])
                vel[1] = ai_velocity * np.sin(att[2])
                
            # Basic Kinematic Integration
            new_pos = pos + vel * dt + 0.5 * imu_accel * (dt**2)
            new_vel = vel + imu_accel * dt
            
            # Reconstruct state
            sigmas_pred[i] = np.concatenate([new_pos, new_vel, att])
            
        # Recover mean and covariance from predicted sigma points
        self.x = np.sum(self.Wm[:, None] * sigmas_pred, axis=0)
        
        # Covariance
        self.P = self.Q.copy()
        for i in range(2 * self.n + 1):
            y = sigmas_pred[i] - self.x
            self.P += self.Wc[i] * np.outer(y, y)

    def update_gnss(self, gnss_pos):
        """
        Update step when GNSS measurement is available.
        gnss_pos: [x, y, z] measurement.
        """
        sigmas = self.generate_sigma_points()
        
        # Measurement function: maps state to measurement space (just extract position)
        sigmas_meas = np.zeros((2 * self.n + 1, self.m))
        for i in range(2 * self.n + 1):
            sigmas_meas[i] = sigmas[i, 0:3]
            
        # Mean measurement
        z_pred = np.sum(self.Wm[:, None] * sigmas_meas, axis=0)
        
        # Measurement Covariance
        P_zz = self.R.copy()
        for i in range(2 * self.n + 1):
            y = sigmas_meas[i] - z_pred
            P_zz += self.Wc[i] * np.outer(y, y)
            
        # Cross Covariance
        P_xz = np.zeros((self.n, self.m))
        for i in range(2 * self.n + 1):
            dx = sigmas[i] - self.x
            dz = sigmas_meas[i] - z_pred
            P_xz += self.Wc[i] * np.outer(dx, dz)
            
        # Kalman Gain
        K = np.dot(P_xz, np.linalg.inv(P_zz))
        
        # Update State and Covariance
        y = gnss_pos - z_pred
        self.x = self.x + np.dot(K, y)
        self.P = self.P - np.dot(K, np.dot(P_zz, K.T))

if __name__ == "__main__":
    ukf = GNSS_INS_UKF()
    print("Initial State:", ukf.x)
    
    # Simulate Prediction (IMU only)
    dt = 0.1
    imu_accel = np.array([0.5, 0.0, 0.0]) # Accelerating in X
    ukf.predict(dt, imu_accel)
    print("State after IMU predict:", ukf.x)
    
    # Simulate GNSS Update
    gnss_meas = np.array([0.1, 0.0, 0.0])
    ukf.update_gnss(gnss_meas)
    print("State after GNSS update:", ukf.x)
    
    # Simulate GNSS Blackout (using AI velocity)
    print("\n-- GNSS Blackout --")
    ai_vel = 5.0 # AI predicts 5m/s forward
    ukf.predict(dt, imu_accel, ai_velocity=ai_vel)
    print("State after AI Dead Reckoning predict:", ukf.x)
