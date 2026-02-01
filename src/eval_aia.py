"""
Average Incremental Accuracy (AIA) Evaluation

Standard metric used in continual learning literature for fair comparison.
Formula: AIA = (1/T) * Σ A_t
where A_t = accuracy on all seen classes after learning task t
"""

import torch
import json
import argparse
import os
import sys

sys.path.append(os.path.dirname(__file__))
from data_cifar100 import SplitCIFAR100
from model import get_model

def evaluate_aia(checkpoint_dir, output_file='aia_results.json', num_classes=100):
    """
    Compute Average Incremental Accuracy
    
    Args:
        checkpoint_dir: Directory containing model_task{i}.pt files
        output_file: Where to save results
        num_classes: Total number of classes
    
    Returns:
        aia: Average Incremental Accuracy
        accuracies_per_task: List of accuracies after each task
    """
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"Using device: {device}")
    print(f"Computing Average Incremental Accuracy")
    print(f"Checkpoint directory: {checkpoint_dir}")
    
    # Load data
    split_cifar100 = SplitCIFAR100()
    task_loaders, test_loader = split_cifar100.get_loaders(batch_size=128)
    num_tasks = len(task_loaders)
    
    # Model
    model = get_model(num_classes=num_classes).to(device)
    
    accuracies_per_task = []
    task_details = []
    
    for task_id in range(num_tasks):
        # Load checkpoint after task_id
        checkpoint_path = os.path.join(checkpoint_dir, f"model_task{task_id}.pt")
        
        if not os.path.exists(checkpoint_path):
            print(f"Warning: {checkpoint_path} not found, skipping")
            continue
        
        model.load_state_dict(torch.load(checkpoint_path, map_location=device))
        model.eval()
        
        # Test on all classes seen so far
        num_seen_classes = (task_id + 1) * 10  # 10 classes per task
        seen_classes = set(range(num_seen_classes))
        
        print(f"\nTask {task_id}: Testing on {num_seen_classes} classes...")
        
        correct_total = 0
        total_total = 0
        
        # Per-task accuracy tracking
        per_task_correct = [0] * (task_id + 1)
        per_task_total = [0] * (task_id + 1)
        
        with torch.no_grad():
            for x, y in test_loader:
                x, y = x.to(device), y.to(device)
                
                # Only evaluate on seen classes
                mask = torch.tensor([label.item() in seen_classes for label in y], 
                                   device=device)
                if not mask.any():
                    continue
                
                x_filtered = x[mask]
                y_filtered = y[mask]
                
                outputs = model(x_filtered)
                pred = outputs.argmax(dim=1)
                
                correct = (pred == y_filtered).sum().item()
                total = y_filtered.size(0)
                
                correct_total += correct
                total_total += total
                
                # Track per-task accuracy
                for t in range(task_id + 1):
                    task_start = t * 10
                    task_end = (t + 1) * 10
                    task_mask = (y_filtered >= task_start) & (y_filtered < task_end)
                    
                    if task_mask.any():
                        per_task_correct[t] += (pred[task_mask] == y_filtered[task_mask]).sum().item()
                        per_task_total[t] += task_mask.sum().item()
        
        # Compute accuracy on all seen classes
        acc = correct_total / total_total if total_total > 0 else 0
        accuracies_per_task.append(acc)
        
        # Compute per-task accuracies
        task_accs = []
        for t in range(task_id + 1):
            if per_task_total[t] > 0:
                t_acc = per_task_correct[t] / per_task_total[t]
                task_accs.append(t_acc)
            else:
                task_accs.append(0)
        
        print(f"  Overall on {num_seen_classes} classes: {acc:.4f}")
        print(f"  Per-task: {[f'{a:.3f}' for a in task_accs]}")
        
        task_details.append({
            'task_id': task_id,
            'num_seen_classes': num_seen_classes,
            'overall_accuracy': acc,
            'per_task_accuracies': task_accs
        })
    
    # Compute Average Incremental Accuracy
    aia = sum(accuracies_per_task) / len(accuracies_per_task) if accuracies_per_task else 0
    
    # Compute final accuracy (on all classes after last task)
    final_acc = accuracies_per_task[-1] if accuracies_per_task else 0
    
    # Compute forgetting (1 - average of early tasks)
    if len(accuracies_per_task) > 1:
        early_avg = sum(accuracies_per_task[:-1]) / (len(accuracies_per_task) - 1)
        forgetting = 1.0 - early_avg
    else:
        early_avg = 0
        forgetting = 1.0
    
    print(f"\n{'='*60}")
    print(f"Average Incremental Accuracy (AIA): {aia:.4f}")
    print(f"Final Task Accuracy: {final_acc:.4f}")
    print(f"Early Tasks Average: {early_avg:.4f}")
    print(f"Forgetting: {forgetting:.4f}")
    print(f"{'='*60}")
    
    # Save results
    results = {
        'average_incremental_accuracy': aia,
        'final_task_accuracy': final_acc,
        'early_tasks_average': early_avg,
        'forgetting': forgetting,
        'accuracies_per_task': accuracies_per_task,
        'task_details': task_details
    }
    
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', 
               exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    return aia, accuracies_per_task

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint_dir', type=str, required=True,
                       help='Directory containing model checkpoints')
    parser.add_argument('--output', type=str, default='aia_results.json',
                       help='Output JSON file')
    parser.add_argument('--num_classes', type=int, default=100,
                       help='Total number of classes')
    args = parser.parse_args()
    
    evaluate_aia(args.checkpoint_dir, args.output, args.num_classes)
