import torch
import torch.nn as nn

class SpeedVibrationFilter1DCNN(nn.Module):
    """
    A 1D-CNN model designed to estimate forward velocity from IMU signals 
    (accelerometer & gyroscope) and filter out high-frequency road noise.
    """
    def __init__(self, num_channels=6, sequence_length=100, hidden_dim=64):
        super(SpeedVibrationFilter1DCNN, self).__init__()
        
        # Expects input of shape: (batch_size, num_channels, sequence_length)
        # num_channels = 6 (Accel X, Y, Z + Gyro X, Y, Z)
        
        self.conv_block1 = nn.Sequential(
            nn.Conv1d(in_channels=num_channels, out_channels=32, kernel_size=5, padding=2),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2)
        )
        
        self.conv_block2 = nn.Sequential(
            nn.Conv1d(in_channels=32, out_channels=64, kernel_size=3, padding=1),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2)
        )
        
        self.conv_block3 = nn.Sequential(
            nn.Conv1d(in_channels=64, out_channels=128, kernel_size=3, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1) # Reduces to (batch_size, 128, 1)
        )
        
        self.fc_layers = nn.Sequential(
            nn.Linear(128, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, 1) # Output is forward velocity (1D)
        )

    def forward(self, x):
        # x shape: (batch, channels, sequence)
        x = self.conv_block1(x)
        x = self.conv_block2(x)
        x = self.conv_block3(x)
        
        # Flatten for fully connected layer
        x = x.view(x.size(0), -1) 
        
        velocity_pred = self.fc_layers(x)
        return velocity_pred

if __name__ == "__main__":
    # Test the model with dummy data
    batch_size = 16
    channels = 6
    seq_len = 100
    
    dummy_input = torch.randn(batch_size, channels, seq_len)
    model = SpeedVibrationFilter1DCNN()
    
    out = model(dummy_input)
    print(f"Input shape: {dummy_input.shape}")
    print(f"Output shape: {out.shape}")
    print(f"Output sample: {out[0].detach().numpy()}")
