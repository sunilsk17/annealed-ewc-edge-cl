#!/bin/bash
# Master script to run ALL remaining CIFAR-100 experiments
# This will run unattended for ~2-3 hours

set -e  # Exit on error

echo "=========================================="
echo "CIFAR-100 REMAINING EXPERIMENTS"
echo "Running: λ=2000, λ=5000, Annealed EWC"
echo "Start time: $(date)"
echo "=========================================="

cd "/Users/sunilkumars/Desktop/EWC Project/drift_cl_edge"
source venv/bin/activate

# λ=2000
echo ""
echo "[1/6] Training λ=2000..."
python src/train_cifar100.py --epochs 10 --lambda_ewc 2000 --save_dir results_cifar100/lambda_sweep/lambda_2000

echo "[2/6] Evaluating λ=2000..."
python src/eval_cifar100.py --checkpoint results_cifar100/lambda_sweep/lambda_2000/model_task9.pt --output results_cifar100/lambda_sweep/lambda_2000_results.json

# λ=5000
echo ""
echo "[3/6] Training λ=5000..."
python src/train_cifar100.py --epochs 10 --lambda_ewc 5000 --save_dir results_cifar100/lambda_sweep/lambda_5000

echo "[4/6] Evaluating λ=5000..."
python src/eval_cifar100.py --checkpoint results_cifar100/lambda_sweep/lambda_5000/model_task9.pt --output results_cifar100/lambda_sweep/lambda_5000_results.json

# Annealed EWC
echo ""
echo "[5/6] Training Annealed EWC (λ_0=5000, inverse decay)..."
python src/train_cifar100_annealed.py --lambda_0 5000 --decay_type inverse --epochs 10 --save_dir checkpoints_cifar100_annealed

echo "[6/6] Evaluating Annealed EWC..."
mkdir -p results_cifar100/annealed_ewc
python src/eval_cifar100.py --checkpoint checkpoints_cifar100_annealed/model_task9.pt --output results_cifar100/annealed_ewc/annealed_results.json

# Aggregate all results
echo ""
echo "Aggregating results..."
python aggregate_cifar100_results.py

# Generate plots
echo ""
echo "Generating plots..."
python src/plot_cifar100_phase_transition.py

echo ""
echo "=========================================="
echo "✓ ALL CIFAR-100 EXPERIMENTS COMPLETE!"
echo "End time: $(date)"
echo "=========================================="
echo ""
echo "Results saved to:"
echo "  - results_cifar100/lambda_sweep/"
echo "  - results_cifar100/annealed_ewc/"
echo ""
