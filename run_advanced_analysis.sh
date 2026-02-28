#!/bin/bash
# Master experiment runner for Q1-level analysis
#
# This script runs all advanced experiments systematically:
# 1. λ-sweep (phase transition)
# 2. Annealed EWC
# 3. Visualization & analysis

set -e  # Exit on error

echo "=========================================="
echo "Q1-Level EWC Analysis - Master Runner"
echo "=========================================="
echo ""

# Activate virtual environment
source venv/bin/activate

# Create results directories
mkdir -p results/lambda_sweep
mkdir -p results/annealed_ewc

echo "[1/3] Running λ-Phase Transition Sweep..."
echo "Testing λ ∈ {0, 200, 500, 1000, 2000, 5000}"
echo "This will take ~2-3 hours..."
echo ""

# Run each lambda value separately to avoid memory issues
for lambda in 0 200 500 1000 2000 5000; do
    echo "  → Training with λ=$lambda..."
    python src/train.py --epochs 10 --lambda_ewc $lambda \
        --save_dir "results/lambda_sweep/lambda_$lambda"
    
    echo "  → Evaluating λ=$lambda..."
    python src/eval_pytorch.py \
        --checkpoint "results/lambda_sweep/lambda_$lambda/model_task4.pt" \
        --output "results/lambda_sweep/lambda_${lambda}_results.json"
    
    echo "  ✓ λ=$lambda complete"
    echo ""
done

echo "[2/3] Running Annealed EWC (λ_t = 5000/(1+t))..."
python src/train_annealed.py --lambda_0 5000 --decay_type inverse \
    --epochs 10 --save_dir checkpoints_annealed

echo "  → Evaluating Annealed EWC..."
python src/eval_pytorch.py \
    --checkpoint checkpoints_annealed/model_task4.pt \
    --output results/annealed_ewc/annealed_results.json

echo "[3/3] Generating visualizations and analysis..."
python src/plot_phase_transition.py

echo ""
echo "=========================================="
echo "✓ All experiments complete!"
echo "=========================================="
echo ""
echo "Results:"
echo "  - Phase transition data: results/lambda_sweep/"
echo "  - Annealed EWC data: results/annealed_ewc/"
echo "  - Plots: results/lambda_sweep/*.png"
echo ""
