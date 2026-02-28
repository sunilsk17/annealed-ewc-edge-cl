"""
λ-Sweep for CIFAR-100

Runs comprehensive hyperparameter sweep across λ values to replicate
CIFAR-10 analysis on the harder CIFAR-100 dataset (10 tasks vs 5).
"""

import subprocess
import json
import os

LAMBDA_VALUES = [0, 200, 500, 1000, 2000, 5000]
EPOCHS = 10
BASE_DIR = "results_cifar100/lambda_sweep"

def run_single_lambda_c100(lambda_val):
    """Run training and evaluation for single λ on CIFAR-100."""
    print(f"\n{'='*60}")
    print(f"CIFAR-100: λ = {lambda_val}")
    print(f"{'='*60}")
    
    save_dir = f"{BASE_DIR}/lambda_{lambda_val}"
    os.makedirs(save_dir, exist_ok=True)
    
    # Train
    print(f"[1/2] Training...")
    train_cmd = [
        "python", "src/train_cifar100.py",
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
    checkpoint = f"{save_dir}/model_task9.pt"  # Task 9 is last task (0-indexed)
    output_json = f"{BASE_DIR}/lambda_{lambda_val}_results.json"
    
    eval_cmd = [
        "python", "src/eval_cifar100.py",
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
    
    print(f"\n✓ λ={lambda_val} Results:")
    print(f"  Final task: {data['final_task']:.4f}")
    print(f"  Early avg:  {data['early_avg']:.4f}")
    print(f"  Forgetting: {data['forgetting']:.4f}")
    
    return data

def main():
    os.makedirs(BASE_DIR, exist_ok=True)
    
    print("="*70)
    print("CIFAR-100 λ-PHASE TRANSITION SWEEP")
    print("="*70)
    print(f"Testing λ ∈ {LAMBDA_VALUES}")
    print(f"Tasks: 10, Epochs per task: {EPOCHS}")
    print("="*70)
    
    all_results = {}
    
    for lambda_val in LAMBDA_VALUES:
        result = run_single_lambda_c100(lambda_val)
        if result:
            all_results[str(lambda_val)] = result
    
    # Save aggregated results
    output_file = f"{BASE_DIR}/sweep_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*70}")
    print(f"✓ CIFAR-100 Sweep complete! Results: {output_file}")
    print(f"{'='*70}")
    
    # Print summary table
    print("\nSUMMARY TABLE:")
    print(f"{'λ':<6} {'Final Task':<12} {'Early Avg':<12} {'Forgetting':<12}")
    print("-" * 50)
    for lam_str in sorted(all_results.keys(), key=lambda x: int(x)):
        data = all_results[lam_str]
        print(f"{lam_str:<6} {data['final_task']:<12.4f} "
              f"{data['early_avg']:<12.4f} {data['forgetting']:<12.4f}")
    
    return all_results

if __name__ == '__main__':
    main()
