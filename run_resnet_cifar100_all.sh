#!/bin/bash
# Master script for ResNet-18 CIFAR-100 experiments
# λ-sweep (0, 200, 500, 1000, 2000, 5000) + Annealed EWC

set -e

echo "=========================================="
echo "ResNet-18 CIFAR-100 EXPERIMENTS"
echo "Running: λ=0, 200, 500, 1000, 2000, 5000 + Annealed"
echo "Start time: $(date)"
echo "Estimated: 4-5 hours"
echo "=========================================="

cd "/Users/sunilkumars/Desktop/EWC Project/drift_cl_edge"
source venv/bin/activate

# λ=0 (Baseline)
echo ""
echo "[1/7] Training λ=0 (Baseline)..."
python src/train_resnet_cifar100.py --epochs 10 --lambda_ewc 0 --save_dir results_resnet_cifar100/lambda_sweep/lambda_0

echo "[1/7] Evaluating λ=0..."
python src/eval_resnet_cifar100.py --checkpoint results_resnet_cifar100/lambda_sweep/lambda_0/model_task9.pt --output results_resnet_cifar100/lambda_sweep/lambda_0_results.json

# λ=200
echo ""
echo "[2/7] Training λ=200..."
python src/train_resnet_cifar100.py --epochs 10 --lambda_ewc 200 --save_dir results_resnet_cifar100/lambda_sweep/lambda_200

echo "[2/7] Evaluating λ=200..."
python src/eval_resnet_cifar100.py --checkpoint results_resnet_cifar100/lambda_sweep/lambda_200/model_task9.pt --output results_resnet_cifar100/lambda_sweep/lambda_200_results.json

# λ=500
echo ""
echo "[3/7] Training λ=500..."
python src/train_resnet_cifar100.py --epochs 10 --lambda_ewc 500 --save_dir results_resnet_cifar100/lambda_sweep/lambda_500

echo "[3/7] Evaluating λ=500..."
python src/eval_resnet_cifar100.py --checkpoint results_resnet_cifar100/lambda_sweep/lambda_500/model_task9.pt --output results_resnet_cifar100/lambda_sweep/lambda_500_results.json

# λ=1000
echo ""
echo "[4/7] Training λ=1000..."
python src/train_resnet_cifar100.py --epochs 10 --lambda_ewc 1000 --save_dir results_resnet_cifar100/lambda_sweep/lambda_1000

echo "[4/7] Evaluating λ=1000..."
python src/eval_resnet_cifar100.py --checkpoint results_resnet_cifar100/lambda_sweep/lambda_1000/model_task9.pt --output results_resnet_cifar100/lambda_sweep/lambda_1000_results.json

# λ=2000
echo ""
echo "[5/7] Training λ=2000..."
python src/train_resnet_cifar100.py --epochs 10 --lambda_ewc 2000 --save_dir results_resnet_cifar100/lambda_sweep/lambda_2000

echo "[5/7] Evaluating λ=2000..."
python src/eval_resnet_cifar100.py --checkpoint results_resnet_cifar100/lambda_sweep/lambda_2000/model_task9.pt --output results_resnet_cifar100/lambda_sweep/lambda_2000_results.json

# λ=5000
echo ""
echo "[6/7] Training λ=5000..."
python src/train_resnet_cifar100.py --epochs 10 --lambda_ewc 5000 --save_dir results_resnet_cifar100/lambda_sweep/lambda_5000

echo "[6/7] Evaluating λ=5000..."
python src/eval_resnet_cifar100.py --checkpoint results_resnet_cifar100/lambda_sweep/lambda_5000/model_task9.pt --output results_resnet_cifar100/lambda_sweep/lambda_5000_results.json

# Annealed EWC
echo ""
echo "[7/7] Training Annealed EWC (λ₀=5000)..."
python src/train_resnet_cifar100_annealed.py --lambda_0 5000 --epochs 10 --save_dir checkpoints_resnet_cifar100_annealed

echo "[7/7] Evaluating Annealed EWC..."
python src/eval_resnet_cifar100.py --checkpoint checkpoints_resnet_cifar100_annealed/model_task9.pt --output results_resnet_cifar100/annealed_ewc/annealed_results.json

echo ""
echo "=========================================="
echo "✓ ResNet-18 CIFAR-100 EXPERIMENTS COMPLETE!"
echo "End time: $(date)"
echo "=========================================="
echo ""
echo "Results saved to: results_resnet_cifar100/"
echo ""
