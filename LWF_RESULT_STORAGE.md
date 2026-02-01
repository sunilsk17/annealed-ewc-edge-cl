# LwF Result Storage Structure

## Directory Organization

```
results_lwf_cifar100/
├── lambda0_aia.json          # Fine-tuning baseline
├── lambda1_aia.json          # Standard LwF
├── lambda2_aia.json          # Higher distillation
├── lambda5_aia.json          # Strong distillation
├── lambda10_aia.json         # Maximum distillation
├── ALL_LWF_RESULTS.json      # Aggregated results
├── LWF_SUMMARY.md            # Human-readable summary
└── COMPARISON_WITH_EWC.md    # Side-by-side comparison

checkpoints_lwf_lambda*/
├── model_task0.pt through model_task9.pt  # 10 checkpoints per λ
```

## What Gets Saved

### Per-Experiment JSON (`lambda*_aia.json`):
```json
{
  "average_incremental_accuracy": 0.XX,
  "final_task_accuracy": 0.XX,
  "early_tasks_average": 0.XX,
  "forgetting": 0.XX,
  "accuracies_per_task": [0.XX, 0.XX, ...],
  "task_details": [
    {
      "task_id": 0,
      "num_seen_classes": 10,
      "overall_accuracy": 0.XX,
      "per_task_accuracies": [0.XX]
    },
    ...
  ]
}
```

### Training Logs:
- `lwf_training_log.txt` - Full training output
- Per-checkpoint metadata in checkpoint directories

### Aggregated Results:
- `ALL_LWF_RESULTS.json` - Master file with all experiments
- `LWF_SUMMARY.md` - Table format for quick reference
- `COMPARISON_WITH_EWC.md` - Direct EWC vs LwF comparison

## Automatic Saving

All results are automatically saved by:
1. `train_lwf_cifar100.py` - Saves checkpoints after each task
2. `eval_aia.py` - Saves AIA metrics in JSON format
3. `aggregate_lwf_results.py` - Combines all results
4. `run_lwf_experiments.sh` - Orchestrates everything

## Verification Checklist

After experiments complete:
- [ ] 5 JSON files in `results_lwf_cifar100/`
- [ ] 50 total checkpoints (5 λ values × 10 tasks)
- [ ] `ALL_LWF_RESULTS.json` exists
- [ ] `LWF_SUMMARY.md` created
- [ ] Training log saved
- [ ] All files backed up

## Recovery

If any results are missing:
```bash
# Recompute AIA for specific checkpoint directory
python src/eval_aia.py --checkpoint_dir checkpoints_lwf_lambda1 --output results_lwf_cifar100/lambda1_aia.json

# Reaggregate all results
python src/aggregate_lwf_results.py
```

## Backup Command

```bash
# Create timestamped backup
DATE=$(date +%Y%m%d_%H%M%S)
cp -r results_lwf_cifar100 results_lwf_backup_$DATE
cp -r checkpoints_lwf_* checkpoints_lwf_backup_$DATE/
```
