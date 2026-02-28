"""
TFLite evaluation script for edge deployment.
Evaluates a quantized .tflite model on all 5 drift environments.
Each environment's full test set is transformed with the corresponding drift augmentation.
"""

import tensorflow as tf
import torch
import numpy as np
import os
from data import DriftCIFAR10, get_transforms


def evaluate_tflite(model_path):
    """Evaluate a .tflite model across all 5 drift environments."""
    print(f"Evaluating TFLite model: {model_path}")
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    input_scale, input_zero_point = input_details[0]['quantization']
    output_scale, output_zero_point = output_details[0]['quantization']

    transforms_list = get_transforms()
    drift_data = DriftCIFAR10()
    loaders, _ = drift_data.get_loaders()

    accuracies = []

    for i, loader in enumerate(loaders):
        print(f"Evaluating on Env {i}...")
        correct = 0
        total = 0

        for x, y in loader:
            curr_batch_size = x.size(0)

            # Quantize to INT8 if required by the model
            if input_details[0]['dtype'] == np.int8:
                x_np = x.numpy().transpose(0, 2, 3, 1)  # NCHW -> NHWC
                input_data = (x_np / input_scale + input_zero_point).astype(np.int8)
            else:
                input_data = x.numpy().transpose(0, 2, 3, 1)

            # Resize interpreter input tensor if batch size differs
            if curr_batch_size != input_details[0]['shape'][0]:
                interpreter.resize_tensor_input(input_details[0]['index'], [curr_batch_size, 32, 32, 3])
                interpreter.allocate_tensors()

            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()
            output = interpreter.get_tensor(output_details[0]['index'])

            pred = output.argmax(axis=1)
            correct += (pred == y.numpy()).sum()
            total += curr_batch_size

        acc = correct / total
        accuracies.append(acc)
        print(f"Env {i} Accuracy: {acc:.4f}")

    return accuracies


if __name__ == '__main__':
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, required=True, help='Path to .tflite model')
    parser.add_argument('--output', type=str, default='results.json', help='Path to output JSON')
    args = parser.parse_args()

    if os.path.exists(args.model):
        accs = evaluate_tflite(args.model)
        print(f"Final Accuracies: {accs}")
        with open(args.output, 'w') as f:
            json.dump({'accuracies': accs}, f)
    else:
        print(f"Model not found: {args.model}")
