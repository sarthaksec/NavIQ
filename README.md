# GNSS-Denied Edge Navigation Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Flutter%20%7C%20iOS%20%7C%20Android-blue.svg)]()
[![AI Framework](https://img.shields.io/badge/AI-PyTorch%20%7C%20ONNX-orange.svg)]()

An enterprise-grade, edge-deployed navigation engine that maintains continuous, lane-level vehicle tracking during complete GPS/GNSS blackouts (e.g., tunnels, urban canyons) using only consumer-grade smartphone IMU sensors.

## 🚀 The Problem with Traditional Dead Reckoning
Standard inertial navigation uses basic physics (double integration of acceleration) to estimate speed. However, microscopic electrical noise in smartphone sensors causes quadratic error accumulation (drift). Within 60 seconds, standard dead reckoning will fail catastrophically.

## 🧠 Our Architecture (The Solution)
This engine discards mathematical integration and replaces it with a **vibration-based acoustic signature model**, fused with advanced non-linear probabilistic filtering.

1. **PCA Gravity Alignment:** A C++ module dynamically isolates the 1g gravity vector to orient the coordinate frame, meaning the phone can be mounted at any angle on the dashboard.
2. **1D-CNN AI Speedometer:** A PyTorch neural network trained on the IO-VNBD dataset. It analyzes 1-second rolling windows of Z/Y axis vibrations (engine RPM, tire-road friction) to infer the absolute forward speed, completely bypassing quadratic drift.
3. **Unscented Kalman Filter (UKF):** Fuses the AI's predicted speed with the gyroscope's yaw rate. It utilizes the Unscented Transform to handle highly non-linear vehicle dynamics (like sudden sharp turns).
4. **HMM Map-Matching:** Utilizes the Viterbi Algorithm against OpenStreetMap vector graphs to probabilistically snap drifting coordinates back to the physical lane.

## ⚡ Edge Execution
The model is quantized to **INT8** and exported to **ONNX**. It runs natively via **Flutter C++ FFI** on the smartphone's Neural Processing Unit (NPU) with sub-15ms latency, requiring absolutely zero cloud connectivity.

## 📂 Repository Structure
- `/ai_engine/`: Core PyTorch training pipeline, Kalman filters, and HMM logic.
- `/ai_engine/scripts/`: Utility scripts used to generate PDFs and diagrams.
- `/mobile_app/`: The Flutter frontend that handles live sensor polling and edge inference.
- `/docs/`: Technical slide decks and system architecture overviews.
- `/media/`: High-resolution data flow diagrams and performance distribution charts.

## 📊 Performance Benchmark
Evaluated against the IO-VNBD independent dataset (Driver B: S-M.csv):
*   **Mean Absolute Error (MAE):** 0.8307 m/s (~2.99 km/h)
*   **Edge Latency:** < 15ms

## 🛠️ How to Run
### 1. Training the AI Model
```bash
cd ai_engine
pip install -r requirements.txt
python train.py
```
This will train the 1D-CNN and export the quantized `model_int8.onnx` to the `/weights/` directory.

### 2. Running the Edge Simulation
```bash
python simulate.py
```
This runs the full UKF + HMM pipeline against a recorded trajectory, verifying the ONNX model's performance without deploying to a physical phone.

---
*Built initially for the Smart India Hackathon (SIH) 2026.*
