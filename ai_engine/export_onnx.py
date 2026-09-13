import torch
from model import SpeedVibrationFilter1DCNN
import os

def export_model_to_onnx(model_path="weights/speed_filter_model.pth", onnx_path="weights/speed_filter.onnx"):
    print(f"Loading PyTorch model from {model_path}...")
    
    # Initialize the model
    model = SpeedVibrationFilter1DCNN()
    
    # Check if weights exist (for dummy testing, we might just export an untrained one)
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path))
        print("Weights loaded successfully.")
    else:
        print(f"Warning: {model_path} not found. Exporting untrained model.")
        
    model.eval()

    # Dummy input matching the expected input shape: (batch_size, num_channels, sequence_length)
    # Batch size 1 for inference
    dummy_input = torch.randn(1, 6, 100)

    print(f"Exporting to {onnx_path}...")
    
    # Export to ONNX
    os.makedirs(os.path.dirname(onnx_path), exist_ok=True)
    
    torch.onnx.export(
        model, 
        dummy_input, 
        onnx_path, 
        export_params=True, 
        opset_version=11,          
        do_constant_folding=True,  
        input_names=['imu_input'],   
        output_names=['velocity_output'], 
        dynamic_axes={'imu_input': {0: 'batch_size'}, 'velocity_output': {0: 'batch_size'}}
    )
    
    print("Export complete. The ONNX model is edge-ready.")

if __name__ == "__main__":
    export_model_to_onnx()
