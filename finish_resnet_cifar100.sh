#!/bin/bash
# Complete remaining ResNet-18 CIFAR-100 experiments
# λ=2000, λ=5000, Annealed EWC

set -e

echo "=========================================="
echo "COMPLETING ResNet-18 CIFAR-100"
echo "Remaining: λ=2000, λ=5000, Annealed"
echo "Start time: $(date)"
echo "Estimated: 2-2.5 hours"
echo "=========================================="

cd "/Users/sunilkumars/Desktop/EWC Project/drift_cl_edge"
source venv/bin/activate

# Clean up incomplete λ=2000
echo ""
echo "Cleaning up incomplete λ=2000..."
rm -rf results_resnet_cifar100/lambda_sweep/lambda_2000

# λ=2000
echo ""
echo "[1/3] Training λ=2000..."
python src/train_resnet_cifar100.py --epochs 10 --lambda_ewc 2000 --save_dir results_resnet_cifar100/lambda_sweep/lambda_2000

echo "[1/3] Evaluating λ=2000..."
python src/eval_resnet_cifar100.py --checkpoint results_resnet_cifar100/lambda_sweep/lambda_2000/model_task9.pt --output results_resnet_cifar100/lambda_sweep/lambda_2000_results.json

# λ=5000
echo ""
echo "[2/3] Training λ=5000..."
python src/train_resnet_cifar100.py --epochs 10 --lambda_ewc 5000 --save_dir results_resnet_cifar100/lambda_sweep/lambda_5000

echo "[2/3] Evaluating λ=5000..."
python src/eval_resnet_cifar100.py --checkpoint results_resnet_cifar100/lambda_sweep/lambda_5000/model_task9.pt --output results_resnet_cifar100/lambda_sweep/lambda_5000_results.json

# Annealed EWC
echo ""
echo "[3/3] Training Annealed EWC (λ₀=5000)..."
python src/train_resnet_cifar100_annealed.py --lambda_0 5000 --epochs 10 --save_dir checkpoints_resnet_cifar100_annealed

echo "[3/3] Evaluating Annealed EWC..."
python src/eval_resnet_cifar100.py --checkpoint checkpoints_resnet_cifar100_annealed/model_task9.pt --output results_resnet_cifar100/annealed_ewc/annealed_results.json

echo ""
echo "=========================================="
echo "✓ ALL ResNet-18 CIFAR-100 EXPERIMENTS COMPLETE!"
echo "End time: $(date)"
echo "=========================================="
echo ""
echo "Results saved to: results_resnet_cifar100/"
echo ""
