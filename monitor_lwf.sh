#!/bin/bash
# Monitor current LwF training progress and ensure results are saved

CHECKPOINT_DIR="checkpoints_lwf_test"
LOG_FILE="lwf_training_log.txt"

echo "=========================================="
echo "LwF Training Monitor"
echo "Time: $(date)"
echo "=========================================="

# Check if training is running
if ps aux | grep -v grep | grep "train_lwf_cifar100.py" > /dev/null; then
    echo "✓ Training is RUNNING"
else
    echo "⚠ Training not detected (may have completed)"
fi

# Check log file
if [ -f "$LOG_FILE" ]; then
    echo ""
    echo "Last 20 lines of training log:"
    echo "---"
    tail -20 "$LOG_FILE"
    echo "---"
else
    echo "⚠ Log file not found: $LOG_FILE"
fi

# Check checkpoints
if [ -d "$CHECKPOINT_DIR" ]; then
    CHECKPOINT_COUNT=$(ls "$CHECKPOINT_DIR"/model_task*.pt 2>/dev/null | wc -l)
    echo ""
    echo "Checkpoints saved: $CHECKPOINT_COUNT/10"
    
    if [ $CHECKPOINT_COUNT -gt 0 ]; then
        echo "Latest checkpoint:"
        ls -lht "$CHECKPOINT_DIR"/model_task*.pt | head -1
    fi
else
    echo "⚠ Checkpoint directory not found: $CHECKPOINT_DIR"
fi

# Estimate completion
if [ -f "$LOG_FILE" ]; then
    CURRENT_TASK=$(grep -c "^Training on Task" "$LOG_FILE" || echo "0")
    echo ""
    echo "Progress: Task $CURRENT_TASK/10"
    
    if [ $CURRENT_TASK -gt 0 ]; then
        PERCENT=$((CURRENT_TASK * 10))
        echo "Completion: ~${PERCENT}%"
    fi
fi

echo ""
echo "=========================================="
echo "To monitor live: tail -f $LOG_FILE"
echo "=========================================="
