import asyncio
import websockets
import json
import pandas as pd
import torch
import time
import numpy as np
from model import SpeedVibrationFilter1DCNN
from ukf import GNSS_INS_UKF
from map_matching import MapMatchingHMM

async def stream_simulation(websocket):
    print("Client connected!")
    
    # 1. Load the Model
    device = torch.device("cpu")
    model = SpeedVibrationFilter1DCNN().to(device)
    model.eval()
    
    # 2. Load the Dataset
    csv_path = r"../IO-VNBD/Synchronised V abd S datasets/Categorised IOVNB Dataset/M (Driver B)/S-M.csv"
    df = pd.read_csv(csv_path, encoding='latin1')
    df.columns = df.columns.str.replace(r'[^a-zA-Z0-9_ \(\)/-]', '', regex=True)
    
    accel_cols = [c for c in df.columns if 'ACCELEROMETER' in c]
    gyro_cols = [c for c in df.columns if 'GYROSCOPE' in c]
    speed_col = [c for c in df.columns if 'GPS SPEED' in c][0]
    
    df = df.dropna(subset=accel_cols + gyro_cols + [speed_col])
    
    imu_data = df[accel_cols + gyro_cols].values
    gt_speed = df[speed_col].values * (1000 / 3600)
    
    # 3. Setup UKF and Map-Matching
    ukf = GNSS_INS_UKF()
    hmm = MapMatchingHMM()
    
    sequence_length = 100
    fps = 30
    sleep_time = 1.0 / fps
    
    # Start at a fake origin
    x, y = 0.0, 0.0
    
    print("Starting simulation stream...")
    # Stream data infinitely
    while True:
        for i in range(0, len(imu_data) - sequence_length, 10):
            # Prepare 1D-CNN Input
            seq = imu_data[i:i+sequence_length]
            inputs = torch.tensor(seq, dtype=torch.float32).unsqueeze(0).permute(0, 2, 1)
            
            # Predict Speed
            with torch.no_grad():
                pred_speed = model(inputs).item()
                
            actual_speed = gt_speed[i+sequence_length-1]
            
            # Dead Reckoning Update
            dt = 10.0 / fps # Time step scaled for visibility
            x += pred_speed * dt
            y += 0.0 # Moving strictly along X for this basic simulation
            
            # Add artificial drift proportional to speed
            drift = np.sin(i * 0.01) * 2.0
            noisy_y = y + drift
            
            # Simulate Map Matching (Snap to Y=0 lane)
            # Using a simplistic threshold to represent HMM snapping back to lane
            snapped_y = 0.0 if abs(noisy_y) < 2.5 else noisy_y
            
            packet = {
                "time_step": i,
                "gt_speed": actual_speed * 3.6, # km/h
                "ai_speed": pred_speed * 3.6, # km/h
                "position": {"x": x, "y": noisy_y},
                "snapped_position": {"x": x, "y": snapped_y}
            }
            
            try:
                await websocket.send(json.dumps(packet))
                await asyncio.sleep(sleep_time)
            except websockets.exceptions.ConnectionClosed:
                print("Client disconnected.")
                return

async def main():
    async with websockets.serve(stream_simulation, "localhost", 8765):
        print("WebSocket Server running on ws://localhost:8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
