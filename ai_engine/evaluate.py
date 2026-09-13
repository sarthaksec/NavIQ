import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from model import SpeedVibrationFilter1DCNN
from train import IMUDataset

def evaluate_and_plot():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Evaluating on device: {device}")

    # Load model
    model = SpeedVibrationFilter1DCNN().to(device)
    weights_path = "weights/speed_filter_model.pth"
    if not os.path.exists(weights_path):
        print(f"Error: Model weights not found at {weights_path}. Please train the model first.")
        return
        
    model.load_state_dict(torch.load(weights_path, map_location=device))
    model.eval()

    # Load a subset of dataset for evaluation
    data_dir = "../IO-VNBD"
    dataset = IMUDataset(data_dir=data_dir, sequence_length=100)
    
    # We will evaluate on the first 500 sequences to make the graph readable
    eval_samples = min(500, len(dataset))
    inputs = dataset.imu_data[:eval_samples].to(device)
    ground_truth = dataset.velocity_data[:eval_samples].numpy()

    # Predict
    with torch.no_grad():
        predictions = model(inputs).cpu().numpy()

    # Calculate errors
    absolute_errors = np.abs(predictions - ground_truth)
    mae = np.mean(absolute_errors)
    
    print(f"Mean Absolute Error (MAE): {mae:.4f} m/s")

    # --- Plot 1: Line Graph (Predictions vs Ground Truth) ---
    plt.figure(figsize=(12, 6))
    plt.plot(ground_truth, label="Ground Truth (GPS Speed)", color='blue', linewidth=2)
    plt.plot(predictions, label="AI Predicted Speed (1D-CNN)", color='red', linestyle='dashed', linewidth=2)
    plt.title("AI Velocity Prediction vs Ground Truth (GNSS)")
    plt.xlabel("Time Sequence (100ms intervals)")
    plt.ylabel("Velocity (m/s)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("prediction_vs_truth.png", dpi=150)
    print("Saved prediction_vs_truth.png")
    
    # --- Plot 2: Bar Chart (Absolute Error Distribution) ---
    plt.figure(figsize=(10, 6))
    plt.hist(absolute_errors, bins=30, color='orange', edgecolor='black')
    plt.title("Distribution of Absolute Prediction Errors")
    plt.xlabel("Absolute Error (m/s)")
    plt.ylabel("Frequency")
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig("error_distribution.png", dpi=150)
    print("Saved error_distribution.png")

if __name__ == "__main__":
    evaluate_and_plot()
