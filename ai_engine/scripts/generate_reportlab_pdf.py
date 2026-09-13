from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor

def generate_pdf(filename):
    doc = SimpleDocTemplate(filename, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        textColor=HexColor('#2c3e50'),
        alignment=1
    )
    
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10,
        textColor=HexColor('#2980b9')
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        leading=14
    )
    
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        leftIndent=20,
        leading=14
    )

    Story = []

    Story.append(Paragraph("Technical Architecture: GNSS-Denied Navigation Engine", title_style))
    Story.append(Paragraph("<b>Detailed Module Specifications & Implementation Guide</b>", ParagraphStyle(name='SubTitle', parent=title_style, fontSize=12, textColor=HexColor('#7f8c8d'))))
    Story.append(Spacer(1, 12))

    Story.append(Paragraph("1. Data Ingestion & Gravity Alignment (PCA)", heading_style))
    Story.append(Paragraph("A critical challenge in smartphone-based dead reckoning is arbitrary device orientation. We must transform the sensor readings from the local device frame to the global vehicular frame.", body_style))
    Story.append(Paragraph("• <b>Hardware Polling:</b> We sample the 3-axis Accelerometer and 3-axis Gyroscope at a strict 100Hz frequency.", bullet_style))
    Story.append(Paragraph("• <b>Principal Component Analysis (PCA):</b> Over a sliding 2-second window, we apply PCA to the accelerometer data. Because Earth's gravity (1g) acts as a constant strong force, the principal eigenvector (highest variance/magnitude) represents the exact gravity vector.", bullet_style))
    Story.append(Paragraph("• <b>Coordinate Rotation:</b> By extracting this gravity vector, we compute a rotational quaternion. We multiply incoming IMU data by this quaternion to continuously rotate the device's data frame so that the Z-axis aligns strictly with vertical gravity and the Y-axis aligns with the forward vehicular motion, neutralizing any tilt, pitch, or roll of the smartphone.", bullet_style))

    Story.append(Paragraph("2. 1D-CNN Velocity Estimation", heading_style))
    Story.append(Paragraph("Traditional double-integration of acceleration (a = dv/dt) accumulates exponential drift within seconds due to sensor noise (bias instability and random walk). To solve this, we bypass mathematical integration and deploy a deep learning model to infer speed directly from vibration frequencies.", body_style))
    Story.append(Paragraph("• <b>Input Features:</b> The network takes a sliding 1-second window (100 samples) of the rotated Z-axis (road bumps/vertical oscillation) and Y-axis (engine/forward vibrations).", bullet_style))
    Story.append(Paragraph("• <b>Architecture:</b> The model is a 1-Dimensional Convolutional Neural Network (1D-CNN). It consists of 3 sequential Conv1D layers (e.g., 64, 128, and 64 filters) with kernel sizes of 3, followed by ReLU activations and MaxPooling1D layers to extract hierarchical vibration features.", bullet_style))
    Story.append(Paragraph("• <b>Output:</b> The extracted feature maps are flattened and passed through a Dense output layer with a linear activation function, predicting the absolute scalar forward velocity (m/s) of the vehicle. This acts as our drift-free, AI-powered speedometer.", bullet_style))

    Story.append(Paragraph("3. Kinematic Sensor Fusion (UKF)", heading_style))
    Story.append(Paragraph("We possess the absolute velocity from the 1D-CNN and angular yaw rates from the Gyroscope. To compute continuous (X,Y) spatial coordinates, we employ an Unscented Kalman Filter (UKF) which handles highly non-linear vehicle dynamics significantly better than standard Extended Kalman Filters (EKF) by using the Unscented Transform.", body_style))
    Story.append(Paragraph("• <b>State Vector:</b> The internal state tracked is [x, y, v, theta, omega], representing Cartesian coordinates, velocity, heading angle, and yaw rate.", bullet_style))
    Story.append(Paragraph("• <b>Prediction Step:</b> The UKF predicts the next state using the non-linear bicycle kinematic model.", bullet_style))
    Story.append(Paragraph("• <b>Update Step:</b> The UKF ingests the 1D-CNN velocity estimate and the Gyroscope's yaw rate as the 'Observation Vector'. It computes the Kalman Gain and updates the state covariance matrix, aggressively smoothing out instantaneous AI mispredictions or gyroscope noise spikes to output a highly stable trajectory path.", bullet_style))

    Story.append(Paragraph("4. Map-Matching (Hidden Markov Model & Viterbi)", heading_style))
    Story.append(Paragraph("Even the UKF will exhibit minor lateral drift over prolonged GNSS blackouts (e.g., drifting 5 meters laterally over a 2km tunnel). To achieve sub-meter lane-level accuracy, we snap the raw UKF coordinates to a known road network.", body_style))
    Story.append(Paragraph("• <b>Hidden States & Observations:</b> The actual road segments are the 'hidden states'. The drifting (X,Y) UKF outputs are the 'observations'.", bullet_style))
    Story.append(Paragraph("• <b>Emission Probability:</b> Modeled as a Gaussian distribution based on the perpendicular geometric distance from the observed (X,Y) point to the nearest road segment edge.", bullet_style))
    Story.append(Paragraph("• <b>Transition Probability:</b> The likelihood of a vehicle transitioning from Road Segment A to Segment B, derived from the road graph topology (vehicles cannot jump across disconnected roads).", bullet_style))
    Story.append(Paragraph("• <b>Viterbi Algorithm:</b> We utilize dynamic programming (Viterbi) to find the most probable sequence of hidden states (true road segments) that generated our observed drifting path. This mathematically locks the vehicle's position to the center of the correct lane.", bullet_style))

    Story.append(Paragraph("5. Edge Deployment & Optimization", heading_style))
    Story.append(Paragraph("The entire computational pipeline runs locally on the smartphone to comply with the zero-latency, GNSS-denied requirement.", body_style))
    Story.append(Paragraph("• <b>Model Quantization:</b> The PyTorch 1D-CNN is exported to ONNX format and quantized from FP32 (32-bit float) down to INT8 (8-bit integer). This slashes memory footprint by 75% and significantly accelerates inference on the mobile Neural Processing Unit (NPU) or Hexagon DSP.", bullet_style))
    Story.append(Paragraph("• <b>Flutter & FFI:</b> The mobile application is built in Flutter (Dart). The heavy matrix multiplications required for PCA and UKF are written in native C++ and invoked asynchronously via Flutter's Foreign Function Interface (FFI) to guarantee real-time execution (sub-15ms latency) without thermal throttling the smartphone.", bullet_style))

    doc.build(Story)

if __name__ == '__main__':
    output_path = r'C:\Users\sarth\.gemini\antigravity-ide\brain\764d65f3-fa9a-4279-a465-a77cf4a0457a\technical_architecture_deep_dive.pdf'
    generate_pdf(output_path)
    print(f"Deeply technical PDF successfully generated at {output_path}")
