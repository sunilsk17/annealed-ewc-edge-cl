"""
Comprehensive result aggregation and storage for LwF experiments
Ensures all results are saved and organized
"""

import json
import os
import glob
from datetime import datetime

def aggregate_lwf_results(base_dir='results_lwf_cifar100'):
    """
    Aggregate all LwF experiment results into a master JSON file
    """
    results = {
        'experiment_type': 'Learning without Forgetting (LwF)',
        'architecture': 'MobileNetV3',
        'dataset': 'CIFAR-100',
        'timestamp': datetime.now().isoformat(),
        'experiments': {}
    }
    
    # Find all result files
    result_files = glob.glob(f"{base_dir}/*_aia.json")
    
    for result_file in result_files:
        # Extract lambda value from filename
        basename = os.path.basename(result_file)
        lambda_key = basename.replace('_aia.json', '')
        
        # Load results
        with open(result_file, 'r') as f:
            data = json.load(f)
        
        results['experiments'][lambda_key] = data
        print(f"Loaded: {lambda_key}")
    
    # Save aggregated results
    output_file = f"{base_dir}/ALL_LWF_RESULTS.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nAggregated results saved to: {output_file}")
    
    # Create human-readable summary
    summary_file = f"{base_dir}/LWF_SUMMARY.md"
    with open(summary_file, 'w') as f:
        f.write("# LwF Results Summary\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Results by λ_distill\n\n")
        f.write("| λ_distill | AIA | Final Task | Early Avg | Forgetting |\n")
        f.write("|-----------|-----|------------|-----------|------------|\n")
        
        for lambda_key in sorted(results['experiments'].keys()):
            exp = results['experiments'][lambda_key]
            aia = exp.get('average_incremental_accuracy', 0)
            final = exp.get('final_task_accuracy', 0)
            early = exp.get('early_tasks_average', 0)
            forgetting = exp.get('forgetting', 0)
            
            f.write(f"| {lambda_key} | {aia:.4f} | {final:.4f} | {early:.4f} | {forgetting:.4f} |\n")
        
        f.write("\n## Comparison with EWC\n\n")
        f.write("**EWC Results (MobileNetV3 CIFAR-100)**:\n")
        f.write("- λ=0: AIA ~7.3%, Final=73.3%, Early=0.02%\n")
        f.write("- λ=5000: AIA ~6.0%, Final=55.7%, Early=0.43%\n\n")
        f.write("**Key Question**: Does LwF achieve >20% AIA?\n")
    
    print(f"Summary saved to: {summary_file}")
    
    return results

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_dir', type=str, default='results_lwf_cifar100')
    args = parser.parse_args()
    
    aggregate_lwf_results(args.base_dir)
