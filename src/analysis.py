import matplotlib.pyplot as plt
import json
import numpy as np
import os

def plot_drift_analysis(ewc_file='ewc_results.json', baseline_file='baseline_results.json', output_file='drift_curve.png'):
    ewc_acc = []
    baseline_acc = []

    if os.path.exists(ewc_file):
        with open(ewc_file, 'r') as f:
            ewc_acc = json.load(f).get('accuracies', [])
    
    if os.path.exists(baseline_file):
        with open(baseline_file, 'r') as f:
            baseline_acc = json.load(f).get('accuracies', [])

    if not ewc_acc and not baseline_acc:
        print("No data found.")
        return

    # Determine X axis
    length = max(len(ewc_acc), len(baseline_acc))
    envs = ['Clean', 'Fog', 'Night', 'Snow', 'Blur']
    if length > 5:
        envs = [f"Env{i}" for i in range(length)]
    elif length < 5:
        envs = envs[:length]

    plt.figure(figsize=(10, 6))
    
    if ewc_acc:
        plt.plot(envs[:len(ewc_acc)], ewc_acc, 'o-', linewidth=2, label=f'EWC-CL (Final: {ewc_acc[-1]:.2%})')
    
    if baseline_acc:
        plt.plot(envs[:len(baseline_acc)], baseline_acc, 's--', linewidth=2, label=f'Static Baseline (Final: {baseline_acc[-1]:.2%})')
    
    plt.title('Accuracy Retention under Concept Drift (MobileNetV3-Small Int8)')
    plt.ylabel('Accuracy')
    plt.xlabel('Drift Environment')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.ylim(0, 1.0)
    
    # Add PAC-Bayes Bound Annotations
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    textstr = r'$\epsilon \leq \hat{\epsilon} + \sqrt{\frac{KL(Q||P) + \ln(n/\delta)}{2n-1}}$'
    plt.text(0.05, 0.05, textstr, transform=plt.gca().transAxes, fontsize=12,
             verticalalignment='bottom', bbox=props)
    
    plt.legend()
    plt.savefig(output_file)
    print(f"Analysis plot saved to {output_file}")

if __name__ == '__main__':
    plot_drift_analysis()
