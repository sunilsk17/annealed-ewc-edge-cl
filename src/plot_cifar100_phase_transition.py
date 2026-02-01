"""
Plot CIFAR-100 Phase Transition

Creates publication-quality plots for CIFAR-100 experiments.
"""

import matplotlib.pyplot as plt
import json
import numpy as np
import os

def plot_cifar100_phase_transition(results_file='results_cifar100/lambda_sweep/sweep_results.json',
                                   output_dir='results_cifar100/lambda_sweep'):
    """Create phase transition plots from CIFAR-100 λ-sweep."""
    
    if not os.path.exists(results_file):
        print(f"Results file not found: {results_file}")
        return
    
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Extract data
    lambda_vals = []
    final_acc = []
    avg_forgetting = []
    early_task_avg = []
    
    for lambda_str, data in sorted(results.items(), key=lambda x: int(x[0])):
        lambda_vals.append(int(lambda_str))
        final_acc.append(data['final_task'])
        avg_forgetting.append(data['forgetting'])
        early_task_avg.append(data['early_avg'])
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Final Task Accuracy vs λ
    ax1.plot(lambda_vals, final_acc, 'o-', linewidth=2, markersize=8, color='#2E86AB')
    ax1.axvline(x=1000, color='red', linestyle='--', alpha=0.5, label='Expected optimal')
    ax1.set_xlabel('λ (EWC Penalty Strength)', fontsize=12)
    ax1.set_ylabel('Final Task Accuracy', fontsize=12)
    ax1.set_title('CIFAR-100: λ-Phase Transition (Final Task)', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Plot 2: Early Task Retention vs λ
    ax2.plot(lambda_vals, early_task_avg, 's-', linewidth=2, markersize=8,
             color='#A23B72', label='Early Task Avg')
    ax2.plot(lambda_vals, [1-f for f in avg_forgetting], '^-', linewidth=2, markersize=8,
             color='#F18F01', label='Retention (1-forgetting)')
    ax2.axvline(x=1000, color='red', linestyle='--', alpha=0.5)
    ax2.set_xlabel('λ (EWC Penalty Strength)', fontsize=12)
    ax2.set_ylabel('Accuracy', fontsize=12)
    ax2.set_title('CIFAR-100: Early Task Retention', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'cifar100_phase_transition.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"CIFAR-100 phase transition plot saved to {output_path}")
    plt.close()
    
    return lambda_vals, final_acc, avg_forgetting

if __name__ == '__main__':
    plot_cifar100_phase_transition()
