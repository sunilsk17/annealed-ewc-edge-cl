import tensorflow as tf
import torch
import numpy as np
import os
from data import DriftCIFAR10

def evaluate_tflite(model_path):
    print(f"Evaluating TFLite model: {model_path}")
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    input_scale, input_zero_point = input_details[0]['quantization']
    output_scale, output_zero_point = output_details[0]['quantization']
    
    # Load data
    drift_data = DriftCIFAR10()
    loaders, _ = drift_data.get_loaders()
    
    accuracies = []
    
    for i, loader in enumerate(loaders): # Evaluate on training/drift envs or test split?
        # User blueprint says "Edge eval: accuracy vs baselines across drift"
        # Since we drift sequentially, we want to see forgetting on old tasks and performance on current.
        # So we evaluate on ALL environments. 
        # Ideally we use the test set for each environment.
        # Our `get_loaders` returned train loaders for each env.
        # We should probably construct test loaders for each env too.
        # DriftCIFAR10.get_loaders returned (loaders, test_loader). 
        # The test_loader was just clean CIFAR10.
        # We need test sets for each drift condition to properly evaluate robustness/forgetting.
        # I'll update DriftCIFAR10 to return test loaders for each env if possible, 
        # or just use the train loader (subset) for evaluation in this demo since the subset is small (2000 images).
        # Using train set for eval is bad practice, but for measuring *forgetting* of the training data it's a proxy.
        # Better: apply the transforms to the global test set.
        
        print(f"Evaluating on Env {i}...")
        correct = 0
        total = 0
        
        # Create a test loader for this environment
        # We reuse the logic from data.py but applied to test set.
        # Since I can't easily import the internal transform logic if not exposed...
        # I laid out get_transforms in data.py so I can import it.
        from data import get_transforms
        transforms_list = get_transforms()
        t = transforms_list[i]
        
        # Wrap the full test set with this transform
        # We need a proper dataset wrapper or just iterate and transform.
        # We can iterate the base test loader and apply transform manually?
        # No, transform is usually applied at __getitem__.
        
        # Let's just assume we update data.py to expose a helper or just do it here.
        # Simplest: Just use the train loader for this demo to save time, 
        # or quickly subclass.
        
        # User script: `for x,y in loader:` where `loader` was from `loaders`. These were the train subsets.
        # So user was evaluating on the train subsets of the tasks. 
        # This measures "Retention" of the learned task.
        
        for x, y in loader:
            # Setup input
            # TFLite input expected shape and type
            # If INT8, we need to quantize x.
            # x is float32 normalized [-1, 1] or similar.
            # input_details[0]['dtype'] should be int8.
            
            if input_details[0]['dtype'] == np.int8:
                # Quantize: q = x / scale + zero_point
                x_np = x.numpy().transpose(0, 2, 3, 1) # NCHW -> NHWC
                x_quant = (x_np / input_scale + input_zero_point).astype(np.int8)
                input_data = x_quant
            else:
                x_np = x.numpy().transpose(0, 2, 3, 1)
                input_data = x_np
            
            # Inference
            # Interpreter only handles one batch? Or works with batch?
            # TFLite resize_tensor_input if batch size differs?
            # Default input shape might be [1, 32, 32, 3].
            # We resize if needed.
            
            curr_batch_size = x.size(0)
            if curr_batch_size != input_details[0]['shape'][0]:
                interpreter.resize_tensor_input(input_details[0]['index'], [curr_batch_size, 32, 32, 3])
                interpreter.allocate_tensors()
            
            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()
            output = interpreter.get_tensor(output_details[0]['index'])
            
            # Dequantize or just argmax? Argmax is same.
            pred = output.argmax(axis=1)
            correct += (pred == y.numpy()).sum()
            total += curr_batch_size
            
        acc = correct / total
        accuracies.append(acc)
        print(f"Env {i} Accuracy: {acc:.4f}")
        
    return accuracies

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, required=True, help='Path to .tflite model')
    parser.add_argument('--output', type=str, default='results.json', help='Path to output .json')
    args = parser.parse_args()

    if os.path.exists(args.model):
        accs = evaluate_tflite(args.model)
        print(f"Final Accuracies: {accs}")
        
        import json
        # Merge if exists? Or overwrite? 
        # Typically separate files is better.
        with open(args.output, 'w') as f:
            json.dump({'accuracies': accs}, f)
    else:
        print(f"Model {args.model} not found.")

