#!/bin/bash
# Enhanced LwF automation with comprehensive result saving
# Ensures all results are stored and backed up

set -e

echo "=========================================="
echo "LwF Experiments - Enhanced Version"
echo "Saves all results, checkpoints, and logs"
echo "Start time: $(date)"
echo "=========================================="

cd "/Users/sunilkumars/Desktop/EWC Project/drift_cl_edge"
source venv/bin/activate

# Create results and backup directories
mkdir -p results_lwf_cifar100
mkdir -p lwf_backups

# Create experiment metadata
cat > results_lwf_cifar100/EXPERIMENT_INFO.txt << EOF
Experiment: Learning without Forgetting on MobileNetV3 CIFAR-100
Start Time: $(date)
Architecture: MobileNetV3 (310k params)
Dataset: CIFAR-100 (10 tasks, 10 classes each)
Method: Knowledge Distillation (Temperature=2.0)
Lambda Values: [0, 1, 2, 5, 10]
Comparison: vs EWC (parameter regularization)
EOF

# Function to save experiment
save_experiment() {
    local lambda_val=$1
    local lambda_dir=$2
    
    echo ""
    echo "[$lambda_val] Training with λ_distill=$lambda_val..."
    python src/train_lwf_cifar100.py \
        --epochs 10 \
        --lambda_distill $lambda_val \
        --save_dir $lambda_dir \
        2>&1 | tee results_lwf_cifar100/training_lambda${lambda_val}.log
    
    echo "[$lambda_val] Evaluating..."
    python src/eval_aia.py \
        --checkpoint_dir $lambda_dir \
        --output results_lwf_cifar100/lambda${lambda_val}_aia.json \
        2>&1 | tee results_lwf_cifar100/eval_lambda${lambda_val}.log
    
    # Verify checkpoint count
    CHECKPOINT_COUNT=$(ls $lambda_dir/model_task*.pt 2>/dev/null | wc -l)
    echo "[$lambda_val] Saved $CHECKPOINT_COUNT checkpoints"
    
    # Save metadata
    cat > results_lwf_cifar100/lambda${lambda_val}_meta.txt << METAEOF
Lambda: $lambda_val
Checkpoints: $CHECKPOINT_COUNT
Checkpoint Directory: $lambda_dir
Training Log: results_lwf_cifar100/training_lambda${lambda_val}.log
Eval Log: results_lwf_cifar100/eval_lambda${lambda_val}.log
Results: results_lwf_cifar100/lambda${lambda_val}_aia.json
Completed: $(date)
METAEOF
    
    echo "[$lambda_val] ✓ Complete and saved"
}

# Run all experiments
save_experiment 0 checkpoints_lwf_lambda0
save_experiment 1 checkpoints_lwf_lambda1
save_experiment 2 checkpoints_lwf_lambda2
save_experiment 5 checkpoints_lwf_lambda5
save_experiment 10 checkpoints_lwf_lambda10

# Aggregate results
echo ""
echo "Aggregating all results..."
python src/aggregate_lwf_results.py --base_dir results_lwf_cifar100

# Create backup
BACKUP_NAME="lwf_backup_$(date +%Y%m%d_%H%M%S)"
echo ""
echo "Creating backup: $BACKUP_NAME"
mkdir -p lwf_backups/$BACKUP_NAME
cp -r results_lwf_cifar100 lwf_backups/$BACKUP_NAME/
cp -r checkpoints_lwf_* lwf_backups/$BACKUP_NAME/

# Final summary
echo ""
echo "=========================================="
echo "✓ ALL LwF EXPERIMENTS COMPLETE!"
echo "End time: $(date)"
echo "=========================================="
echo ""
echo "Results Location:"
echo "  - Individual: results_lwf_cifar100/lambda*_aia.json"
echo "  - Aggregated: results_lwf_cifar100/ALL_LWF_RESULTS.json"
echo "  - Summary: results_lwf_cifar100/LWF_SUMMARY.md"
echo "  - Backup: lwf_backups/$BACKUP_NAME"
echo ""
echo "Checkpoint Count:"
ls checkpoints_lwf_*/model_task*.pt 2>/dev/null | wc -l | xargs echo "  Total checkpoints:"
echo ""
echo "Next Steps:"
echo "  1. Review results_lwf_cifar100/LWF_SUMMARY.md"
echo "  2. Compare with EWC results"
echo "  3. Update paper if AIA > 20%"
echo ""
