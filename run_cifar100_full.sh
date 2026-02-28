#!/bin/bash
# Master automation script for CIFAR-100 experiments
#
# Runs complete λ-sweep + annealed EWC for cross-dataset validation

set -e

echo "=========================================="
echo "CIFAR-100 CONTINUAL LEARNING EXPERIMENTS"
echo "=========================================="
echo "Start time: $(date)"
echo ""

cd "$(dirname "$0")"
source venv/bin/activate

# Create results directory
mkdir -p results_cifar100/lambda_sweep
mkdir -p results_cifar100/annealed_ewc

echo "[1/7] Running λ-sweep on CIFAR-100..."
echo "λ ∈ {0, 200, 500, 1000, 2000, 5000}"
echo "This will take ~4-5 hours..."
echo ""

# Run each lambda value
for lambda in 0 200 500 1000 2000 5000; do
    echo "  → Training λ=$lambda..."
    python src/train_cifar100.py --epochs 10 --lambda_ewc $lambda \
        --save_dir "results_cifar100/lambda_sweep/lambda_$lambda"
    
    echo "  → Evaluating λ=$lambda..."
    python src/eval_cifar100.py \
        --checkpoint "results_cifar100/lambda_sweep/lambda_$lambda/model_task9.pt" \
        --output "results_cifar100/lambda_sweep/lambda_${lambda}_results.json"
    
    echo "  ✓ λ=$lambda complete"
    echo ""
done

echo "[2/7] Running Annealed EWC on CIFAR-100..."
python src/train_cifar100_annealed.py --lambda_0 5000 --decay_type inverse \
    --epochs 10 --save_dir checkpoints_cifar100_annealed

echo "  → Evaluating Annealed EWC..."
python src/eval_cifar100.py \
    --checkpoint checkpoints_cifar100_annealed/model_task9.pt \
    --output results_cifar100/annealed_ewc/annealed_results.json

echo "[3/7] Aggregating results..."
python aggregate_cifar100_results.py

echo "[4/7] Generating plots..."
python src/plot_cifar100_phase_transition.py

echo "[5/7] Creating comparison analysis..."
python compare_datasets.py

echo "[6/7] Generating paper-ready documentation..."
python generate_cifar100_docs.py

echo "[7/7] Done!"
echo ""
echo "=========================================="
echo "✓ All CIFAR-100 experiments complete!"
echo "=========================================="
echo "End time: $(date)"
echo ""
echo "Results:"
echo "  - Raw data: results_cifar100/"
echo "  - Documentation: result_docs_cifar100/"
echo "  - Cross-dataset comparison: results/cross_dataset_comparison/"
echo ""
