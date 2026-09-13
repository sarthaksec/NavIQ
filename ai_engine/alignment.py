import numpy as np
from sklearn.decomposition import PCA

class InVehicleAlignment:
    """
    Determines the smartphone's orientation (pitch, roll, yaw) relative to the 
    vehicle's driving direction.
    """
    def __init__(self):
        self.pca = PCA(n_components=3)
        self.rotation_matrix = np.eye(3)
        self.is_calibrated = False

    def calibrate(self, accel_data, threshold=1.0):
        """
        Calibrates the alignment using accelerometer data during an initial 
        acceleration phase of the vehicle.
        
        Args:
            accel_data (np.ndarray): Shape (N, 3), containing X, Y, Z accel readings.
            threshold (float): Minimum variance required to confirm movement.
        """
        if len(accel_data) < 50:
            print("Not enough data for calibration.")
            return False
            
        # Subtract gravity (assuming the mean is mostly gravity when stationary)
        # For a moving vehicle, a low-pass filter should be used first to extract gravity.
        gravity = np.mean(accel_data, axis=0)
        gravity_norm = gravity / np.linalg.norm(gravity)
        
        # Remove gravity component to isolate linear acceleration
        linear_accel = accel_data - gravity
        
        # Check if there is enough movement to calibrate
        if np.var(np.linalg.norm(linear_accel, axis=1)) < threshold:
            print("Variance too low. Vehicle must be accelerating forward to calibrate.")
            return False

        # Use PCA to find the direction of maximum variance (forward axis)
        self.pca.fit(linear_accel)
        forward_axis = self.pca.components_[0]
        
        # Ensure forward axis is orthogonal to gravity (assuming flat ground)
        forward_axis = forward_axis - np.dot(forward_axis, gravity_norm) * gravity_norm
        forward_axis = forward_axis / np.linalg.norm(forward_axis)
        
        # Right axis is cross product of forward and gravity
        right_axis = np.cross(forward_axis, gravity_norm)
        right_axis = right_axis / np.linalg.norm(right_axis)
        
        # Recompute forward to ensure perfect orthogonality
        forward_axis = np.cross(gravity_norm, right_axis)
        
        # Construct rotation matrix from phone frame to vehicle frame
        # Vehicle frame: X=Right, Y=Forward, Z=Up (Gravity is -Z)
        self.rotation_matrix = np.vstack([right_axis, forward_axis, -gravity_norm])
        self.is_calibrated = True
        
        print("Calibration successful.")
        return True

    def align(self, sensor_data):
        """
        Aligns raw sensor data from the phone's frame to the vehicle's frame.
        
        Args:
            sensor_data (np.ndarray): Shape (N, 3), e.g., Accel or Gyro data.
            
        Returns:
            np.ndarray: Aligned sensor data.
        """
        if not self.is_calibrated:
            raise ValueError("Must run calibrate() before align()")
            
        # Apply rotation matrix
        return np.dot(sensor_data, self.rotation_matrix.T)

if __name__ == "__main__":
    # Test with dummy data
    aligner = InVehicleAlignment()
    # Simulate phone sitting on dashboard facing forward, accelerating
    # Gravity mostly on Z, acceleration mostly on Y
    dummy_accel = np.random.normal(loc=[0, 2.0, 9.8], scale=0.5, size=(100, 3))
    
    success = aligner.calibrate(dummy_accel)
    if success:
        print("Rotation Matrix:")
        print(aligner.rotation_matrix)
        
        aligned_data = aligner.align(dummy_accel)
        print("Aligned Data Mean (should have ~9.8 on Z and ~2.0 on Y):")
        print(np.mean(aligned_data, axis=0))
