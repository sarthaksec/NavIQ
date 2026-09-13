import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from model import SpeedVibrationFilter1DCNN
import os

class IMUDataset(Dataset):
    def __init__(self, data_dir, sequence_length=100):
        """
        Parses the IO-VNBD smartphone data (e.g., S-M.csv) to train the velocity predictor.
        """
        self.sequence_length = sequence_length
        csv_path = os.path.join(data_dir, "Synchronised V abd S datasets", "Categorised IOVNB Dataset", "M (Driver B)", "S-M.csv")
        
        print(f"Loading dataset from {csv_path}...")
        import pandas as pd
        df = pd.read_csv(csv_path, encoding='latin1')
        
        # Clean headers by replacing special characters
        df.columns = df.columns.str.replace(r'[^a-zA-Z0-9_ \(\)/-]', '', regex=True)
        
        # Inputs: Accel X, Y, Z and Gyro Yaw, Pitch, Roll
        # The columns are approximately:
        # ACCELEROMETER X (m/s), ACCELEROMETER Y (m/s), ACCELEROMETER Z (m/s)
        # GYROSCOPE Yaw (rad/s), GYROSCOPE Pitch (rad/s), GYROSCOPE Roll (rad/s)
        accel_cols = [c for c in df.columns if 'ACCELEROMETER' in c]
        gyro_cols = [c for c in df.columns if 'GYROSCOPE' in c]
        
        # Target: GPS SPEED (converted from km/h to m/s)
        speed_col = [c for c in df.columns if 'GPS SPEED' in c][0]
        
        # Drop rows with NaN in critical columns
        df = df.dropna(subset=accel_cols + gyro_cols + [speed_col])
        
        imu_data = df[accel_cols + gyro_cols].values
        velocity_data = df[speed_col].values * (1000 / 3600) # Convert km/h to m/s

        
        # Chunk into sequences
        self.num_samples = len(imu_data) // sequence_length
        
        # Shape: (num_samples, channels=6, sequence_length)
        self.imu_data = torch.tensor(imu_data[:self.num_samples * sequence_length], dtype=torch.float32)
        self.imu_data = self.imu_data.view(self.num_samples, sequence_length, 6).permute(0, 2, 1)
        
        # Target velocity is the velocity at the end of the sequence
        velocity_targets = velocity_data[:self.num_samples * sequence_length]
        self.velocity_data = torch.tensor(velocity_targets.reshape(self.num_samples, sequence_length)[:, -1], dtype=torch.float32).unsqueeze(1)
        
        print(f"Dataset loaded: {self.num_samples} sequences created.")

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        return self.imu_data[idx], self.velocity_data[idx]

def train_model(epochs=10, batch_size=32, learning_rate=0.001):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")

    # Initialize model, loss, and optimizer
    model = SpeedVibrationFilter1DCNN().to(device)
    criterion = nn.MSELoss() # Mean Squared Error for regression (velocity prediction)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Load dataset
    # TODO: Point to the actual IO-VNBD dataset directory after it finishes downloading
    dataset = IMUDataset(data_dir="../IO-VNBD")
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    
    # Set up live plotting
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title("Live Training Loss (Per Batch)")
    ax.set_xlabel("Batch Steps")
    ax.set_ylabel("Loss (MSE)")
    line, = ax.plot([], [], 'b-', linewidth=1, label="Training Loss")
    ax.legend(loc="upper right")
    ax.grid(True)
    
    batch_steps = []
    loss_data = []
    global_step = 0

    print("Starting training loop...")
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for i, (inputs, targets) in enumerate(dataloader):
            inputs, targets = inputs.to(device), targets.to(device)

            # Zero gradients
            optimizer.zero_grad()

            # Forward pass
            outputs = model(inputs)
            loss = criterion(outputs, targets)

            # Backward pass and optimize
            loss.backward()
            optimizer.step()

            loss_val = loss.item()
            running_loss += loss_val
            
            # Update live plot every 10 batches
            if i % 10 == 0:
                global_step += 10
                batch_steps.append(global_step)
                loss_data.append(loss_val)
                line.set_xdata(batch_steps)
                line.set_ydata(loss_data)
                ax.relim()
                ax.autoscale_view()
                plt.pause(0.01)
        
        avg_loss = running_loss / len(dataloader)
        print(f"Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.4f}")

    print("Training complete!")
    plt.ioff()
    plt.show()
    
    # Save the model
    os.makedirs("weights", exist_ok=True)
    torch.save(model.state_dict(), "weights/speed_filter_model.pth")
    print("Model saved to weights/speed_filter_model.pth")

if __name__ == "__main__":
    train_model(epochs=5)
