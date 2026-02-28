"""
λ-Sweep Experiment Script

This script performs a comprehensive hyperparameter sweep of λ_EWC to identify
the phase transition point between underfitting (catastrophic forgetting) and
overfitting (catastrophic rigidity).

Key contribution: Demonstrates that EWC undergoes a sharp phase transition
under edge constraints, not just gradual degradation.
"""

import torch
import json
import os
import sys
import argparse
from train import train_model
from eval_pytorch import evaluate_pytorch

# Lambda sweep configuration
LAMBDA_VALUES = [0, 200, 500, 1000, 2000, 5000]
EPOCHS = 15
SAVE_DIR_BASE = "results/lambda_sweep"

def run_lambda_sweep(epochs=15):
    """
    Run training for all λ values and collect results.
    
    Returns:
        dict: Results for each λ value
    """
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    results = {}
    
    for lambda_val in LAMBDA_VALUES:
        print(f"\n{'='*60}")
        print(f"Running experiment with λ = {lambda_val}")
        print(f"{'='*60}\n")
        
        save_dir = f"{SAVE_DIR_BASE}/lambda_{lambda_val}"
        os.makedirs(save_dir, exist_ok=True)
        
        # Import and run training
        from train import main as train_main
        import sys
        
        # Temporarily modify sys.argv to pass arguments
        old_argv = sys.argv
        sys.argv = ['train.py', 
                    '--epochs', str(epochs),
                    '--lambda_ewc', str(lambda_val),
                    '--save_dir', save_dir]
        
        try:
            train_main()
        except SystemExit:
            pass
        finally:
            sys.argv = old_argv
        
        # Evaluate
        checkpoint_path = f"{save_dir}/model_task4.pt"
        if os.path.exists(checkpoint_path):
            accuracies = evaluate_pytorch(checkpoint_path, device)
            
            # Calculate metrics
            final_task_acc = accuracies[-1]
            # Average forgetting: how much accuracy dropped on tasks 0-3
            avg_forgetting = 1.0 - sum(accuracies[:-1]) / len(accuracies[:-1])
            
            results[lambda_val] = {
                'accuracies': accuracies,
                'final_task_accuracy': final_task_acc,
                'average_forgetting': avg_forgetting,
                'early_task_avg': sum(accuracies[:-1]) / len(accuracies[:-1])
            }
            
            print(f"\nResults for λ={lambda_val}:")
            print(f"  Final task accuracy: {final_task_acc:.4f}")
            print(f"  Average forgetting: {avg_forgetting:.4f}")
            print(f"  Early tasks avg: {results[lambda_val]['early_task_avg']:.4f}")
        else:
            print(f"Warning: Checkpoint not found at {checkpoint_path}")
    
    # Save all results
    output_file = f"{SAVE_DIR_BASE}/sweep_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Lambda sweep complete! Results saved to {output_file}")
    print(f"{'='*60}")
    
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=15, help='Epochs per task')
    args = parser.parse_args()
    
    results = run_lambda_sweep(epochs=args.epochs)
