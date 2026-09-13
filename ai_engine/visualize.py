import pandas as pd
import matplotlib.pyplot as plt
import os

def visualize_dataset(csv_path):
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path, encoding='latin1')
    
    # Clean headers by replacing special characters
    df.columns = df.columns.str.replace(r'[^a-zA-Z0-9_ \(\)/-]', '', regex=True)
    
    accel_cols = [c for c in df.columns if 'ACCELEROMETER' in c]
    gyro_cols = [c for c in df.columns if 'GYROSCOPE' in c]
    speed_col = [c for c in df.columns if 'GPS SPEED' in c][0]
    
    # Use a small subset to make the graph readable
    subset = df.iloc[1000:2000].reset_index()
    
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    # Plot Accelerometer
    for col in accel_cols:
        axes[0].plot(subset.index, subset[col], label=col.replace('ACCELEROMETER ', ''))
    axes[0].set_title("Accelerometer Data (m/s²)")
    axes[0].set_ylabel("Acceleration")
    axes[0].legend(loc='upper right')
    axes[0].grid(True)
    
    # Plot Gyroscope
    for col in gyro_cols:
        axes[1].plot(subset.index, subset[col], label=col.replace('GYROSCOPE ', ''))
    axes[1].set_title("Gyroscope Data (rad/s)")
    axes[1].set_ylabel("Angular Velocity")
    axes[1].legend(loc='upper right')
    axes[1].grid(True)
    
    # Plot GPS Speed
    axes[2].plot(subset.index, subset[speed_col], color='red', label="GPS Speed (km/h)", linewidth=2)
    axes[2].set_title("Ground Truth Speed (GPS)")
    axes[2].set_ylabel("Speed (km/h)")
    axes[2].set_xlabel("Time Step")
    axes[2].legend(loc='upper right')
    axes[2].grid(True)
    
    plt.tight_layout()
    
    out_file = "dataset_visualization.png"
    plt.savefig(out_file, dpi=150)
    print(f"Visualization saved to {out_file}")

if __name__ == "__main__":
    csv_file = r"../IO-VNBD/Synchronised V abd S datasets/Categorised IOVNB Dataset/M (Driver B)/S-M.csv"
    if os.path.exists(csv_file):
        visualize_dataset(csv_file)
    else:
        print("Dataset not found. Please ensure it is fully downloaded.")
