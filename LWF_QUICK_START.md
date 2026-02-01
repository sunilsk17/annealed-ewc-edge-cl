# LwF Implementation for MobileNetV3 - Quick Start

## What We're Testing

**Hypothesis**: If LwF (distillation) gets >10% retention where EWC (parameter regularization) gets 0%, we prove rigidity is **EWC-specific**, not a general capacity issue.

---

## Files Created

1. **`src/train_lwf_cifar100.py`** - LwF training with knowledge distillation
2. **`src/eval_aia.py`** - Average Incremental Accuracy evaluation
3. **`run_lwf_experiments.sh`** - Automation script

---

## Quick Start - Run Single Experiment

### Critical Test (λ_distill=1):
```bash
cd "/Users/sunilkumars/Desktop/EWC Project/drift_cl_edge"
source venv/bin/activate

# Train with standard LwF
python src/train_lwf_cifar100.py --epochs 10 --lambda_distill 1 --save_dir checkpoints_lwf_test

# Evaluate with AIA metric
python src/eval_aia.py --checkpoint_dir checkpoints_lwf_test --output lwf_test_results.json
```

**Time**: ~40-50 minutes

---

## Full Sweep - All λ_distill Values

```bash
cd "/Users/sunilkumars/Desktop/EWC Project/drift_cl_edge"
caffeinate -d -i -s bash run_lwf_experiments.sh
```

**Tests**:
- λ_distill = 0 (fine-tuning baseline)
- λ_distill = 1 (standard LwF)
- λ_distill = 2
- λ_distill = 5
- λ_distill = 10

**Time**: ~4 hours total

---

## What to Look For

### Success Criteria:
**If LwF AIA > 20%**:
- ✅ Proves distillation works where parameter regularization fails
- ✅ Isolates EWC's rigidity as specific to Fisher-based methods
- ✅ **Major contribution**: "Parameter regularization fails, distillation succeeds"

### Baseline Comparison:
**EWC Results (MobileNetV3 CIFAR-100)**:
- λ=0: AIA ~7.3%, Final=73.3%, Early=0.02%
- λ=5000: AIA ~6.0%, Final=55.7%, Early=0.43%

**Expected LwF**:
- λ_distill=1: AIA ~20-40% (estimated), better retention

---

## Understanding Metrics

### Average Incremental Accuracy (AIA):
- Formula: AIA = (1/T) Σ A_t
- A_t = accuracy on all seen classes after task t
- **Standard literature metric** - enables direct comparison

### Why AIA Matters:
- EWC papers don't report this consistently
- FeTrIL/PASS use AIA as primary metric
- Your results will be directly comparable

---

## Next Steps

### After First LwF Run (λ_distill=1):

**If AIA > 20%**:
1. Run full sweep (5 λ values)
2. Compare to EWC systematically
3. Update paper with "distillation vs regularization" narrative

**If AIA < 10%**:
- Still valuable (shows capacity issue more fundamental)
- Focus on "edge models struggle period" framing
- Skip full sweep, document finding

---

## Timeline

### Minimum (1 week):
- Day 1-2: Single LwF run (λ_distill=1)
- Day 3: Compute AIA for existing EWC experiments
- Day 4-5: Analysis and comparison
- Day 6-7: Update paper

### Full (2 weeks):
- Week 1: LwF sweep + AIA standardization
- Week 2: Analysis, plots, paper updates

---

## Expected Paper Impact

### Before:
- "EWC exhibits catastrophic rigidity"
- NeurIPS ~40-50% acceptance

### After (if LwF works):
- "Parameter regularization fails, distillation works better"
- Isolates failure mechanism
- NeurIPS ~60-70% acceptance

---

**Ready to start? Run the single test first to validate the hypothesis!**
