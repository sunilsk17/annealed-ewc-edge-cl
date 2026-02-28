"""
Evaluation script for ResNet-18 models on CIFAR-100
"""

import torch
import json
import argparse
import os
import sys

sys.path.append(os.path.dirname(__file__))
from data_cifar100 import SplitCIFAR100
from model_resnet import get_resnet18_cifar

def evaluate_resnet_cifar100(checkpoint_path, output_file='resnet_cifar100_results.json'):
    """
    Evaluate ResNet-18 model on all CIFAR-100 tasks.
    
    Args:
        checkpoint_path: Path to model checkpoint
        output_file: JSON file to save results
        
    Returns:
        accuracies: List of accuracies for each task
    """
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load model
    model = get_resnet18_cifar(num_classes=100).to(device)
    model.load_state_dict(torch.load(checkpoint_path, map_location=device))
    model.eval()
    
    # Load data
    split_cifar100 = SplitCIFAR100()
    task_loaders, _ = split_cifar100.get_loaders(batch_size=128)
    
    accuracies = []
    
    with torch.no_grad():
        for task_id, (_, task_classes) in enumerate(task_loaders):
            # Get test data for this task
            _, test_subset, _ = split_cifar100.get_task_data(task_id)
            test_loader = torch.utils.data.DataLoader(
                test_subset, batch_size=128, shuffle=False
            )
            
            print(f"Evaluating on Task {task_id} (Classes: {task_classes.tolist()})...")
            
            correct = 0
            total = 0
            
            for x, y in test_loader:
                x, y = x.to(device), y.to(device)
                output = model(x)
                pred = output.argmax(dim=1)
                correct += (pred == y).sum().item()
                total += y.size(0)
            
            acc = correct / total
            accuracies.append(acc)
            print(f"Task {task_id} Accuracy: {acc:.4f}")
    
    # Calculate metrics
    avg_acc = sum(accuracies) / len(accuracies)
    final_acc = accuracies[-1]
    early_avg = sum(accuracies[:-1]) / (len(accuracies) - 1) if len(accuracies) > 1 else 0
    
    print(f"\n{'='*60}")
    print(f"Final Accuracies: {[f'{a:.4f}' for a in accuracies]}")
    print(f"Average Accuracy: {avg_acc:.4f}")
    print(f"Final Task: {final_acc:.4f}")
    print(f"Early Tasks Avg: {early_avg:.4f}")
    print(f"{'='*60}")
    
    # Save results
    results = {
        'accuracies': accuracies,
        'average': avg_acc,
        'final_task': final_acc,
        'early_avg': early_avg,
        'forgetting': 1.0 - early_avg
    }
    
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to {output_file}")
    
    return accuracies

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', type=str, required=True, 
                       help='Path to model checkpoint')
    parser.add_argument('--output', type=str, default='resnet_cifar100_results.json',
                       help='Output JSON file')
    args = parser.parse_args()
    
    evaluate_resnet_cifar100(args.checkpoint, args.output)
