"""
Efficient λ-Sweep Runner with JSON Aggregation

Runs all λ values and aggregates results for phase transition analysis.
"""

import subprocess
import json
import os
import sys

LAMBDA_VALUES = [0, 200, 500, 1000, 2000, 5000]
EPOCHS = 10  # Reduced from 15 for faster iteration
BASE_DIR = "results/lambda_sweep"

def run_single_lambda(lambda_val):
    """Run training and evaluation for a single λ value."""
    print(f"\n{'='*60}")
    print(f"λ = {lambda_val}")
    print(f"{'='*60}")
    
    save_dir = f"{BASE_DIR}/lambda_{lambda_val}"
    os.makedirs(save_dir, exist_ok=True)
    
    # Train
    print(f"[1/2] Training...")
    train_cmd = [
        "python", "src/train.py",
        "--epochs", str(EPOCHS),
        "--lambda_ewc", str(lambda_val),
        "--save_dir", save_dir
    ]
    
    result = subprocess.run(train_cmd, capture_output=False)
    if result.returncode != 0:
        print(f"ERROR: Training failed for λ={lambda_val}")
        return None
    
    # Evaluate
    print(f"[2/2] Evaluating...")
    checkpoint = f"{save_dir}/model_task4.pt"
    output_json = f"{BASE_DIR}/lambda_{lambda_val}_results.json"
    
    eval_cmd = [
        "python", "src/eval_pytorch.py",
        "--checkpoint", checkpoint,
        "--output", output_json
    ]
    
    result = subprocess.run(eval_cmd, capture_output=False)
    if result.returncode != 0:
        print(f"ERROR: Evaluation failed for λ={lambda_val}")
        return None
    
    # Load results
    with open(output_json, 'r') as f:
        data = json.load(f)
    
    accuracies = data['accuracies']
    final_acc = accuracies[-1]
    early_avg = sum(accuracies[:-1]) / len(accuracies[:-1]) if len(accuracies) > 1 else 0
    avg_forgetting = 1.0 - early_avg
    
    result_data = {
        'accuracies': accuracies,
        'final_task_accuracy': final_acc,
        'average_forgetting': avg_forgetting,
        'early_task_avg': early_avg
    }
    
    print(f"\n✓ λ={lambda_val} Results:")
    print(f"  Final task: {final_acc:.4f}")
    print(f"  Early avg:  {early_avg:.4f}")
    print(f"  Forgetting: {avg_forgetting:.4f}")
    
    return result_data

def main():
    os.makedirs(BASE_DIR, exist_ok=True)
    
    print("="*70)
    print("λ-PHASE TRANSITION SWEEP")
    print("="*70)
    print(f"Testing λ ∈ {LAMBDA_VALUES}")
    print(f"Epochs per task: {EPOCHS}")
    print("="*70)
    
    all_results = {}
    
    for lambda_val in LAMBDA_VALUES:
        result = run_single_lambda(lambda_val)
        if result:
            all_results[str(lambda_val)] = result
    
    # Save aggregated results
    output_file = f"{BASE_DIR}/sweep_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*70}")
    print(f"✓ Sweep complete! Results: {output_file}")
    print(f"{'='*70}")
    
    # Print summary table
    print("\nSUMMARY TABLE:")
    print(f"{'λ':<6} {'Final Task':<12} {'Early Avg':<12} {'Forgetting':<12}")
    print("-" * 50)
    for lam_str in sorted(all_results.keys(), key=lambda x: int(x)):
        data = all_results[lam_str]
        print(f"{lam_str:<6} {data['final_task_accuracy']:<12.4f} "
              f"{data['early_task_avg']:<12.4f} {data['average_forgetting']:<12.4f}")
    
    return all_results

if __name__ == '__main__':
    main()
