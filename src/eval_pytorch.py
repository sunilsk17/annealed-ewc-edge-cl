import torch
import torch.nn as nn
import os
import argparse
import json
from data import DriftCIFAR10
from model import get_model

def evaluate_pytorch(model_path, device):
    """Evaluate a PyTorch model on all drift environments."""
    model = get_model(num_classes=10).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    
    # Load data
    drift_data = DriftCIFAR10()
    loaders, test_loader = drift_data.get_loaders()
    
    accuracies = []
    
    with torch.no_grad():
        for i, loader in enumerate(loaders):
            print(f"Evaluating on Env {i}...")
            correct = 0
            total = 0
            
            for x, y in loader:
                x, y = x.to(device), y.to(device)
                output = model(x)
                pred = output.argmax(dim=1)
                correct += (pred == y).sum().item()
                total += y.size(0)
            
            acc = correct / total
            accuracies.append(acc)
            print(f"Env {i} Accuracy: {acc:.4f}")
    
    return accuracies

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', type=str, required=True, help='Path to .pt checkpoint')
    parser.add_argument('--output', type=str, default='results.json', help='Path to output .json')
    args = parser.parse_args()
    
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    if os.path.exists(args.checkpoint):
        accs = evaluate_pytorch(args.checkpoint, device)
        print(f"\nFinal Accuracies: {[f'{a:.4f}' for a in accs]}")
        
        with open(args.output, 'w') as f:
            json.dump({'accuracies': accs}, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        print(f"Checkpoint {args.checkpoint} not found.")
