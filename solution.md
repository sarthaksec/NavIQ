# Proposed Solution: AI-ML Intelligent Dead Reckoning with GNSS Fusion

## 1. Problem summary

The goal is to maintain continuous vehicle navigation during GNSS blackouts using only a smartphone IMU, without relying on an OBD speed feed. The solution must limit dead-reckoning drift to less than 10% of distance travelled, support real-time mobile inference, and also work as an edge-deployable engine with external IMUs.

The key technical difficulty is that raw consumer-phone accelerometer and gyroscope readings cannot be reliably double-integrated. Small orientation errors, sensor bias, vibration, potholes, and phone-mount movement cause position drift to grow rapidly. A successful system therefore needs a hybrid approach: physical navigation constraints and probabilistic fusion, enhanced by machine learning and offline map data.

## 2. Proposed architecture

```text
Phone / external IMU + GNSS
          |
          v
Calibration, alignment, filtering, motion detection
          |
          +--> ML speed and bias-correction model
          |
          v
GNSS-INS fusion filter ---- GNSS unavailable ----> constrained dead reckoning
          |                                          |
          v                                          v
     Reliable trajectory <---- map matching + road/vehicle constraints
```

The system should retain a single navigation state throughout the trip. Instead of abruptly switching between separate GNSS and dead-reckoning systems, it changes the measurements trusted by one fusion filter as GNSS quality changes.

## 3. Functional modules

### 3.1 Sensor preprocessing and phone-to-vehicle alignment

This module standardizes input from phone and external IMUs before navigation processing.

- Normalize timestamps and resample all sensor streams.
- Estimate gravity to establish the vertical axis and phone pitch/roll.
- Estimate vehicle-forward direction from sustained travel and GNSS course while GNSS is reliable.
- Detect phone movement or rotation in its holder and trigger partial recalibration.
- Apply robust low-pass/band-pass filtering and outlier rejection for engine vibration, road bumps, and potholes.

### 3.2 Motion-state classification

A compact model, supplemented by simple physical rules, classifies short IMU windows into:

- stationary or engine idling
- normal forward driving
- accelerating or braking
- turning
- pothole/bump event
- likely phone-mount disturbance

This enables zero-velocity updates while stopped and prevents transient shocks from being treated as sustained vehicle acceleration.

### 3.3 AI-assisted forward-speed estimation

Train a lightweight temporal model using IO-VNBD IMU data and odometry/GNSS-derived ground-truth velocity. Suitable models include a small 1D CNN plus GRU, Temporal Convolutional Network, or a compact Transformer.

**Inputs**

- gravity-aligned accelerometer readings `(ax, ay, az)`
- gyroscope readings `(gx, gy, gz)`
- signal magnitudes and short-window statistical features
- optional previous fused speed and motion state

**Outputs**

- forward speed
- optional predicted confidence/uncertainty
- optional IMU-bias or residual correction

The uncertainty estimate should be supplied to the fusion filter so that the model is trusted less on rough roads, during aggressive driving, or after suspected phone movement.

### 3.4 GNSS-INS fusion engine

Use an Error-State Extended Kalman Filter (ES-EKF) as the main production baseline. It is lightweight, interpretable, and appropriate for real-time mobile inference.

The state should include:

- position
- velocity
- heading/orientation
- accelerometer bias
- gyroscope bias
- optional speed-model residual or scale error

The filter uses:

- IMU propagation at sensor rate
- GNSS position, velocity, and course updates when quality is acceptable
- ML-predicted forward-speed updates
- zero-velocity updates when the vehicle is stationary
- non-holonomic constraints (approximately zero lateral and vertical vehicle velocity)

ML should improve the filter by estimating speed, residual errors, or measurement confidence. The physical fusion filter should remain the principal estimator rather than replacing it with an opaque end-to-end model.

### 3.5 Seamless GNSS-deficit handler

GNSS quality should be assessed with reported accuracy, satellite/geometry indicators where available, innovation residuals, and consistency checks against inertial prediction.

- **Healthy GNSS:** GNSS measurements strongly correct the INS state.
- **Degraded GNSS:** GNSS measurement weight is reduced.
- **GNSS blackout:** GNSS updates stop; the filter continues with IMU propagation, ML speed updates, non-holonomic constraints, stationary updates, and map constraints.
- **GNSS recovery:** GNSS is validated and gradually reintroduced to avoid an abrupt jump in the displayed vehicle position.

### 3.6 Offline map matching

Download an OpenStreetMap road network for the target region and use Hidden Markov Model (HMM) map matching.

For each predicted point:

- find candidate nearby road segments;
- score candidates using position uncertainty and heading alignment;
- score transitions using predicted travel distance, speed, legal road connectivity, and route continuity;
- reject impossible jumps, wrong-way movements, and implausible turns.

Map matching should provide soft observations back to the fusion engine. Merely snapping the displayed marker to a road would hide error rather than correct the actual navigation state.

## 4. Shared mobile and edge engine

The core navigation engine should be sensor-agnostic and receive normalized sensor packets:

```text
timestamp, accelerometer, gyroscope, magnetometer?, GNSS?, sensor quality
```

This permits two adapters while preserving one core implementation:

- Android phone IMU/GNSS adapter, typically operating at 10-100 Hz.
- External IMU adapter, including higher-rate FOG IMUs around 200 Hz.

## 5. Suggested technology choices

| Area | Suggested technology |
|---|---|
| Data processing and model training | Python, PyTorch, IO-VNBD pipeline |
| Fusion research prototype | Python/NumPy or C++ reference implementation |
| Mobile ML inference | TensorFlow Lite or ONNX Runtime Mobile |
| Mobile application | Kotlin with a native C++/Rust navigation core if required |
| Offline road data | OpenStreetMap extract with a compact routing graph |
| Edge-deployable engine | C++ or Python API with configurable sensor adapters |

## 6. Development plan

1. Load, synchronize, and inspect IO-VNBD IMU, odometry, and GNSS records.
2. Implement an ES-EKF/INS baseline and replay dataset trajectories.
3. Add gravity alignment, gyro-bias estimation, zero-velocity updates, and non-holonomic constraints.
4. Train and validate the lightweight forward-speed model.
5. Simulate GNSS blackout intervals at multiple distances and durations.
6. Integrate HMM-based offline map matching as a soft fusion constraint.
7. Export the trained model to a mobile format and build the mobile navigation interface.
8. Package the same core engine for external-IMU/edge use.

## 7. Evaluation methodology

Evaluate simulated GNSS outages of 50 m, 100 m, 500 m, and 1 km. Report:

- drift as a percentage of distance travelled;
- position RMSE and maximum position error;
- forward-speed error;
- heading error;
- position update rate and end-to-end latency;
- recovery behaviour when GNSS returns.

Perform an ablation study to quantify each contribution:

1. Raw INS.
2. INS with non-holonomic and zero-velocity constraints.
3. INS plus the ML speed model.
4. INS plus ML speed model and map matching.

## 8. Important feasibility statement

Lane-level accuracy cannot be guaranteed from a smartphone IMU alone throughout a long unconstrained GNSS outage. It becomes realistic when the system begins with a reliable GNSS state and uses road geometry, route continuity, non-holonomic constraints, and map matching. The application should expose uncertainty internally and avoid presenting an unjustified precision claim.

This hybrid design is practical for the required 10 Hz smartphone target, extensible to high-rate external IMUs, and measurable with the IO-VNBD benchmark.
