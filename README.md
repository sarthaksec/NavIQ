# GNSS-Denied Edge Navigation Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Flutter%20%7C%20iOS%20%7C%20Android-blue.svg)]()
[![AI Framework](https://img.shields.io/badge/AI-PyTorch%20%7C%20ONNX-orange.svg)]()

An enterprise-grade, edge-deployed navigation engine designed to maintain continuous, lane-level vehicle tracking during complete GPS/GNSS blackouts (e.g., tunnels, urban canyons, adversarial jamming environments) using only consumer-grade smartphone IMU sensors.

## 1. The Problem with Traditional Dead Reckoning

Standard inertial navigation systems attempt to track a vehicle's position during a GPS blackout using mathematical Dead Reckoning. This involves taking raw accelerometer data and performing double integration to calculate displacement ($s = 0.5 * a * t^2$). 

However, this approach is fundamentally flawed when using consumer-grade MEMS (Micro-Electro-Mechanical Systems) sensors found in smartphones. These sensors contain microscopic electrical noise. When noise is integrated twice over time, the error accumulates quadratically. Within 60 seconds of a GPS blackout, standard dead reckoning will diverge significantly, resulting in catastrophic navigation failure (e.g., the map showing the vehicle driving through buildings or moving backwards).

## 2. Our Architecture: The Solution

To solve the quadratic drift problem, this engine completely discards mathematical double integration. Instead, it utilizes a hybrid architecture combining a vibration-based acoustic signature model with advanced non-linear probabilistic filtering.

### 2.1. PCA Gravity Alignment
Smartphone placement in a vehicle is entirely arbitrary (e.g., mounted on a dashboard, thrown in a cup holder). A C++ module dynamically isolates the 1g gravity vector using Principal Component Analysis (PCA). It calculates a 3x3 rotation matrix to mathematically rotate the coordinate frame in real-time. This guarantees that the neural network always receives perfectly leveled sensor data, regardless of the device's physical orientation.

### 2.2. 1D-CNN AI Speedometer
A PyTorch neural network analyzes 1-second rolling windows (100 timesteps at 100Hz) of Z/Y axis vibrations. Instead of treating the accelerometer data as a physics vector, the AI treats it as a frequency signature (listening to engine RPM and tire-road friction). The model infers the absolute forward speed of the vehicle directly from these vibrations, completely bypassing quadratic drift.

### 2.3. Unscented Kalman Filter (UKF)
The AI's predicted speed is fused with the gyroscope's yaw rate using an Unscented Kalman Filter. While standard Extended Kalman Filters (EKF) fail under highly non-linear vehicle dynamics (such as sudden, sharp turns), the UKF utilizes the Unscented Transform. This allows the system to accurately track the vehicle's non-linear kinematic trajectory and update the local Cartesian coordinates (X, Y).

### 2.4. HMM Map-Matching
To prevent the drifting coordinates from straying off the road, the system utilizes a Hidden Markov Model (HMM). It applies the Viterbi Algorithm against OpenStreetMap (OSM) vector graphs to probabilistically calculate the most likely physical lane the vehicle is occupying, snapping the coordinates back to reality before rendering the UI.

## 3. Edge Execution and Deployment

This architecture is not reliant on cloud connectivity, which is critical since internet access is typically lost inside tunnels alongside GPS.
- The trained PyTorch model is quantized to an **INT8** precision format, shrinking its memory footprint by 75%.
- The model is exported to the **ONNX** (Open Neural Network Exchange) format.
- It executes natively via **Flutter C++ FFI** on the smartphone's Neural Processing Unit (NPU) or DSP.
- This guarantees sub-15ms latency, allowing the system to poll sensors, run AI inference, and update the UI marker at 60 frames per second on local hardware.

## 4. Repository Structure

- `/ai_engine/`: Contains the core PyTorch training pipeline, data preprocessing, Kalman filter implementations, and the HMM map-matching logic.
- `/ai_engine/scripts/`: Utility scripts used for evaluating the models and generating documentation.
- `/ai_engine/weights/`: The directory where the exported ONNX models are saved post-training.
- `/mobile_app/`: The Flutter frontend application that handles live sensor polling (accelerometer/gyroscope) and edge inference.
- `/docs/`: Technical slide decks and system architecture overviews.
- `/media/`: High-resolution data flow diagrams, error distribution charts, and prediction vs. truth graphs.

## 5. Performance Benchmarks

The AI engine was trained and evaluated against the IO-VNBD (Inertial Odometry Vehicle Navigation Benchmark Dataset), utilizing over 58 hours and 4,400 km of real-world driving data across multiple countries.

Evaluation against the independent test split (Driver B: S-M.csv) yielded the following metrics:
*   **Mean Absolute Error (MAE):** 0.8307 m/s (~2.99 km/h)
*   **Root Mean Square Error (RMSE):** 1.25 m/s
*   **Edge Inference Latency:** < 15ms (Tested on standard mobile NPU hardware)

## 6. Setup and Execution

### 6.1. Training the AI Model
To train the neural network from scratch using the provided dataset:
```bash
cd ai_engine
pip install -r requirements.txt
python train.py
```
This script will preprocess the dataset, train the 1D-CNN, and automatically export the quantized `model_int8.onnx` file into the `/weights/` directory.

### 6.2. Running the Edge Simulation
To verify the UKF and HMM pipeline against a recorded trajectory without deploying to a physical phone:
```bash
cd ai_engine
python simulate.py
```
This runs the complete sensor fusion pipeline, demonstrating how the system recovers coordinates during a simulated GNSS blackout.

---
*Developed for the Smart India Hackathon (SIH) 2026.*
