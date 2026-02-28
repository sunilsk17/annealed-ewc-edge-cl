"""
Aggregate CIFAR-100 λ-sweep results

Collects all λ results and creates summary tables.
"""

import json
import os

def aggregate_cifar100_results(base_dir='results_cifar100/lambda_sweep'):
    """Aggregate all λ-sweep results."""
    lambda_values = [0, 200, 500, 1000, 2000, 5000]
    aggregated = {}
    
    print("="*60)
    print("AGGREGATING CIFAR-100 λ-SWEEP RESULTS")
    print("="*60)
    
    for lambda_val in lambda_values:
        result_file = f"{base_dir}/lambda_{lambda_val}_results.json"
        
        if os.path.exists(result_file):
            with open(result_file, 'r') as f:
                data = json.load(f)
            
            aggregated[str(lambda_val)] = data
            
            print(f"✓ λ={lambda_val:5d}: Final={data['final_task']:.4f}, "
                  f"Early={data['early_avg']:.4f}, Forget={data['forgetting']:.4f}")
        else:
            print(f"✗ λ={lambda_val:5d}: Results not found")
    
    # Save aggregated
    output_file = f"{base_dir}/sweep_results.json"
    with open(output_file, 'w') as f:
        json.dump(aggregated, f, indent=2)
    
    print(f"\n✓ Aggregated results saved to: {output_file}")
    print("="*60)
    
    # Print summary table
    print("\nSUMMARY TABLE:")
    print(f"{'λ':<8} {'Final Task':<12} {'Early Avg':<12} {'Forgetting':<12} {'Avg All':<12}")
    print("-" * 60)
    for lam_str in sorted(aggregated.keys(), key=lambda x: int(x)):
        d = aggregated[lam_str]
        print(f"{lam_str:<8} {d['final_task']:<12.4f} {d['early_avg']:<12.4f} "
              f"{d['forgetting']:<12.4f} {d['average']:<12.4f}")
    
    # Phase transition analysis
    print("\nPHASE TRANSITION ANALYSIS:")
    final_accs = [(int(k), v['final_task']) for k, v in aggregated.items()]
    if len(final_accs) >= 2:
        max_lam, max_acc = max(final_accs, key=lambda x: x[1])
        min_lam, min_acc = min(final_accs, key=lambda x: x[1])
        
        print(f"  Best λ: {max_lam} (Final: {max_acc:.4f})")
        print(f"  Worst λ: {min_lam} (Final: {min_acc:.4f})")
        print(f"  Performance drop: {(max_acc - min_acc):.4f} ({(max_acc-min_acc)/max_acc*100:.1f}%)")
    
    return aggregated

if __name__ == '__main__':
    aggregate_cifar100_results()
