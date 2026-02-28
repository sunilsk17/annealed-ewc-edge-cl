import torch
import torch.nn as nn
import onnx
# from onnx_tf.backend import prepare
import tensorflow as tf
import numpy as np
import os
from model import get_model
from data import DriftCIFAR10

def representative_dataset_gen():
    # Use valid data from the first environment for calibration
    drift_data = DriftCIFAR10()
    loaders, _ = drift_data.get_loaders()
    loader = loaders[0]
    
    for i, (images, _) in enumerate(loader):
        if i > 50: break # Use 50 batches
        # TFLite expects standard list of inputs (often NHWC for TF, NCHW for PyTorch conversion?)
        # When converting from PyTorch via ONNX, the layout often stays NCHW unless transposed.
        # But TensorFlow usually expects NHWC. 
        # onnx2tf typically converts to NHWC.
        # We need to check the input shape of the TF model.
        
        # PyTorch NCHW -> TF NHWC
        # images is [B, C, H, W]
        # Transpose to [B, H, W, C]
        images_nhwc = images.permute(0, 2, 3, 1).numpy()
        yield [images_nhwc]

import subprocess
import shutil

def export_pipeline(model_path, final_tflite_path):
    device = torch.device('cpu') # Export on CPU
    model = get_model(num_classes=10).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    
    # 1. PyTorch -> ONNX
    dummy_input = torch.randn(1, 3, 32, 32)
    onnx_path = model_path.replace('.pt', '.onnx')
    print(f"Exporting to ONNX: {onnx_path}")
    torch.onnx.export(model, dummy_input, onnx_path, opset_version=12, input_names=['input'], output_names=['output'])
    
    # 2. ONNX -> TF SavedModel via onnx2tf
    print("Exporting to TF SavedModel via onnx2tf...")
    tf_path = model_path.replace('.pt', '_tf')
    if os.path.exists(tf_path):
        shutil.rmtree(tf_path)
        
    subprocess.run(['onnx2tf', '-i', onnx_path, '-o', tf_path, '-v', 'error'], check=True)
    
    # 3. TF -> TFLite (INT8)
    print("Converting to TFLite (INT8)...")
    converter = tf.lite.TFLiteConverter.from_saved_model(tf_path)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    
    converter.representative_dataset = representative_dataset_gen
    
    # Ensure input/output is int8 compatible for Micro
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8
    
    tflite_model = converter.convert()
    
    with open(final_tflite_path, 'wb') as f:
        f.write(tflite_model)
        
    print(f"Saved TFLite model to {final_tflite_path}")
    return final_tflite_path

    return final_tflite_path

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', type=str, required=True, help='Path to .pt checkpoint')
    parser.add_argument('--output', type=str, required=True, help='Path to output .tflite')
    args = parser.parse_args()
    
    if os.path.exists(args.checkpoint):
        export_pipeline(args.checkpoint, args.output)
    else:
        print(f"Checkpoint {args.checkpoint} not found.")

