# λ-Sweep Real-Time Results

## Completed Experiments

### λ = 0 (Baseline - No EWC)
- **Final Task**: 58.24%
- **Early Task Avg**: 17.59% (Env 0-3 average)
- **Forgetting**: 82.41%
- **Analysis**: Strong final performance but severe catastrophic forgetting
- **Status**: ✅ Complete
- **File**: `results/lambda_sweep/lambda_0_results.json`

### λ = 200 (Light Regularization)
- **Final Task**: 51.64%
- **Early Task Avg**: 18.40% (Env 0-3 average)  
- **Forgetting**: 81.60%
- **Analysis**: Slight regularization, still dominated by forgetting
- **Status**: ✅ Complete
- **File**: `results/lambda_sweep/lambda_200_results.json`

## In Progress

### λ = 500
- **Status**: 🔄 Training on Task 3/5
- **Progress**: ~60% complete

### λ = 1000
- **Status**: ⏳ Queued

### λ = 2000
- **Status**: ⏳ Queued

### λ = 5000  
- **Status**: ⏳ Queued (already have this from previous experiments - will reuse)

## Preliminary Observations

1. **λ=0 vs λ=200**: Minimal difference (~6% final task drop, ~1% early improvement)
   - Suggests phase transition hasn't started yet
   
2. **Expected Pattern**:
   - Low λ (0-500): Forgetting-dominated, high final task accuracy
   - **Transition zone (500-1500)**: Sharp performance change
   - High λ (2000-5000): Rigidity-dominated, low performance across all tasks

3. **Hypothesis Check**: 
   - ✓ Low λ shows forgetting
   - ⏳ Waiting for transition evidence
   - ✓ High λ (5000) showed rigidity (from previous experiments)

## Next Steps

1. Complete λ ∈ {500, 1000, 2000}
2. Aggregate all results using `aggregate_results.py`
3. Generate phase transition plots
4. Run annealed EWC
5. Finalize Q1 contribution document

---
**Last Updated**: 2026-01-15 09:10 IST  
**Estimated Completion**: ~2 hours remaining
