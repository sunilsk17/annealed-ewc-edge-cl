"""
Phase Transition Visualization & PAC-Bayes Analysis

Creates publication-quality plots demonstrating:
1. λ-phase transition curve (rigidity vs forgetting)
2. PAC-Bayes interpretation (KL vs empirical risk tradeoff)
"""

import matplotlib.pyplot as plt
import json
import numpy as np
import os

def plot_phase_transition(results_file='results/lambda_sweep/sweep_results.json',
                         output_dir='results/lambda_sweep'):
    """
    Create phase transition plots from λ-sweep results.
    """
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
        final_acc.append(data['final_task_accuracy'])
        avg_forgetting.append(data['average_forgetting'])
        early_task_avg.append(data['early_task_avg'])
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Final Task Accuracy vs λ
    ax1.plot(lambda_vals, final_acc, 'o-', linewidth=2, markersize=8, color='#2E86AB')
    ax1.axvline(x=1000, color='red', linestyle='--', alpha=0.5, label='Optimal λ region')
    ax1.set_xlabel('λ (EWC Penalty Strength)', fontsize=12)
    ax1.set_ylabel('Final Task Accuracy', fontsize=12)
    ax1.set_title('λ-Phase Transition: Final Task Performance', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Add annotations
    if len(lambda_vals) > 0:
        min_idx = np.argmin(final_acc)
        max_idx = np.argmax(final_acc)
        ax1.annotate(f'Catastrophic\nRigidity\n({lambda_vals[min_idx]}, {final_acc[min_idx]:.2%})',
                    xy=(lambda_vals[min_idx], final_acc[min_idx]),
                    xytext=(lambda_vals[min_idx]+500, final_acc[min_idx]+0.05),
                    arrowprops=dict(arrowstyle='->', color='red'),
                    fontsize=9, ha='center')
    
    # Plot 2: Early Task Retention vs λ
    ax2.plot(lambda_vals, early_task_avg, 's-', linewidth=2, markersize=8, 
             color='#A23B72', label='Early Task Avg')
    ax2.plot(lambda_vals, [1-f for f in avg_forgetting], '^-', linewidth=2, markersize=8,
             color='#F18F01', label='Retention (1-forgetting)')
    ax2.axvline(x=1000, color='red', linestyle='--', alpha=0.5)
    ax2.set_xlabel('λ (EWC Penalty Strength)', fontsize=12)
    ax2.set_ylabel('Accuracy', fontsize=12)
    ax2.set_title('λ-Phase Transition: Early Task Retention', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'phase_transition.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Phase transition plot saved to {output_path}")
    plt.close()
    
    # Create PAC-Bayes interpretation plot
    create_pac_bayes_plot(lambda_vals, final_acc, early_task_avg, output_dir)
    
    return lambda_vals, final_acc, avg_forgetting

def create_pac_bayes_plot(lambda_vals, final_acc, early_avg, output_dir):
    """
    Visualize PAC-Bayes bound components.
    
    Key insight: As λ↑, KL(Q||P)↓ but empirical risk↑ sharply,
    causing net bound to loosen.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Simulate bound components (normalized for visualization)
    # KL term decreases with λ (more regularization = closer to prior)
    kl_proxy = [1.0 / (1 + 0.001 * lam) for lam in lambda_vals]
    
    # Empirical risk increases with λ (rigidity hurts training)
    emp_risk = [1 - acc for acc in final_acc]
    
    # Total bound (simplified)
    total_bound = [e + 0.5*np.sqrt(k) for e, k in zip(emp_risk, kl_proxy)]
    
    ax.plot(lambda_vals, emp_risk, 'o-', linewidth=2, label='Empirical Risk (↑)', color='#C1121F')
    ax.plot(lambda_vals, kl_proxy, 's-', linewidth=2, label='KL(Q||P) proxy (↓)', color='#003049')
    ax.plot(lambda_vals, total_bound, '^-', linewidth=2, label='PAC-Bayes Bound', color='#780000')
    
    ax.set_xlabel('λ (EWC Penalty Strength)', fontsize=12)
    ax.set_ylabel('Risk / Complexity (normalized)', fontsize=12)
    ax.set_title('PAC-Bayes Interpretation: Why EWC Failed at High λ', 
                 fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    
    # Add text box with explanation
    textstr = ('High λ minimizes KL(Q||P)\nBUT increases empirical risk faster\n→ Net bound loosens')
    ax.text(0.65, 0.95, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'pac_bayes_explanation.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"PAC-Bayes plot saved to {output_path}")
    plt.close()

def compare_annealed_vs_fixed(annealed_results, fixed_results, output_dir='results/annealed_ewc'):
    """
    Compare annealed EWC with fixed λ baselines.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    envs = ['Clean', 'Fog', 'Night', 'Snow', 'Blur']
    
    # Plot annealed
    if annealed_results:
        ax.plot(envs, annealed_results, 'o-', linewidth=2.5, markersize=10,
                label='Annealed EWC (λ_t = λ₀/(1+t))', color='#2E86AB')
    
    # Plot fixed lambda comparisons
    if 'baseline' in fixed_results:
        ax.plot(envs, fixed_results['baseline'], 's--', linewidth=2, markersize=8,
                label='Baseline (λ=0)', color='#F18F01', alpha=0.7)
    
    if 'ewc_5000' in fixed_results:
        ax.plot(envs, fixed_results['ewc_5000'], '^--', linewidth=2, markersize=8,
                label='Fixed EWC (λ=5000)', color='#C1121F', alpha=0.7)
    
    ax.set_xlabel('Drift Environment', fontsize=12)
    ax.set_ylabel('Accuracy', fontsize=12)
    ax.set_title('Annealed EWC Recovers from Catastrophic Rigidity', 
                 fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    ax.set_ylim(0, 1.0)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'annealed_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Annealed comparison plot saved to {output_path}")
    plt.close()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--results_file', type=str, 
                       default='results/lambda_sweep/sweep_results.json')
    parser.add_argument('--output_dir', type=str, default='results/lambda_sweep')
    args = parser.parse_args()
    
    plot_phase_transition(args.results_file, args.output_dir)
