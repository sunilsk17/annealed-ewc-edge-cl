"""
Aggregate Lambda Sweep Results

Collects all λ-sweep results and generates summary tables and JSON.
Ensures no results are lost.
"""

import json
import os
from pathlib import Path

def aggregate_sweep_results(base_dir='results/lambda_sweep'):
    """
    Aggregate all lambda sweep results into a single file.
    
    Returns:
        dict: Aggregated results
    """
    lambda_values = [0, 200, 500, 1000, 2000, 5000]
    aggregated = {}
    
    print("="*60)
    print("AGGREGATING λ-SWEEP RESULTS")
    print("="*60)
    
    for lambda_val in lambda_values:
        result_file = f"{base_dir}/lambda_{lambda_val}_results.json"
        
        if os.path.exists(result_file):
            with open(result_file, 'r') as f:
                data = json.load(f)
            
            accuracies = data['accuracies']
            final_acc = accuracies[-1]
            early_avg = sum(accuracies[:-1]) / len(accuracies[:-1]) if len(accuracies) > 1 else 0
            avg_forgetting = 1.0 - early_avg
            
            aggregated[str(lambda_val)] = {
                'accuracies': accuracies,
                'final_task_accuracy': final_acc,
                'average_forgetting': avg_forgetting,
                'early_task_avg': early_avg
            }
            
            print(f"✓ λ={lambda_val:5d}: Final={final_acc:.4f}, Early={early_avg:.4f}, Forget={avg_forgetting:.4f}")
        else:
            print(f"✗ λ={lambda_val:5d}: Results not found at {result_file}")
    
    # Save aggregated results
    output_file = f"{base_dir}/sweep_results.json"
    with open(output_file, 'w') as f:
        json.dump(aggregated, f, indent=2)
    
    print(f"\n✓ Aggregated results saved to: {output_file}")
    print("="*60)
    
    # Print summary table
    print("\nSUMMARY TABLE:")
    print(f"{'λ':<8} {'Final Task':<12} {'Early Avg':<12} {'Forgetting':<12}")
    print("-" * 50)
    for lam_str in sorted(aggregated.keys(), key=lambda x: int(x)):
        d = aggregated[lam_str]
        print(f"{lam_str:<8} {d['final_task_accuracy']:<12.4f} {d['early_task_avg']:<12.4f} {d['average_forgetting']:<12.4f}")
    
    # Identify phase transition point
    print("\nPHASE TRANSITION ANALYSIS:")
    final_accs = [(int(k), v['final_task_accuracy']) for k, v in aggregated.items()]
    final_accs_sorted = sorted(final_accs, key=lambda x: x[0])
    
    if len(final_accs_sorted) >= 2:
        max_lam, max_acc = max(final_accs_sorted, key=lambda x: x[1])
        min_lam, min_acc = min(final_accs_sorted, key=lambda x: x[1])
        
        print(f"  Best λ: {max_lam} (Final accuracy: {max_acc:.4f})")
        print(f"  Worst λ: {min_lam} (Final accuracy: {min_acc:.4f})")
        print(f"  Performance drop: {(max_acc - min_acc):.4f} ({(max_acc-min_acc)/max_acc*100:.1f}%)")
    
    return aggregated

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_dir', type=str, default='results/lambda_sweep')
    args = parser.parse_args()
    
    aggregate_sweep_results(args.base_dir)
