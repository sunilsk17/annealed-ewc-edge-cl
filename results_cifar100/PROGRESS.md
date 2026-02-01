# CIFAR-100 Experimental Progress Tracker

## Experiment Status: IN PROGRESS (4/7 Running)

**Start Time**: 2026-01-29 20:47 IST  
**Last Updated**: 2026-01-30 06:03 IST

---

## Progress

### ✅ λ = 0 (Baseline) - COMPLETE
- **Final Task**: 73.30%
- **Early Avg**: 0.02%
- **Forgetting**: 99.98%

### ✅ λ = 200 - COMPLETE  
- **Final Task**: 66.70% (-6.60%)
- **Early Avg**: 0.07%
- **Forgetting**: 99.93%

### ✅ λ = 500 - COMPLETE
- **Final Task**: 63.30% (-10.00% total)
- **Early Avg**: 0.11%
- **Forgetting**: 99.89%

### 🔄 λ = 1000 - RUNNING NOW
- **Status**: Task 0 started
- **Expected**: ~40 minutes
- **Started**: 06:03 IST

### ⏳ λ = 2000 - QUEUED
- **Status**: Pending

### ⏳ λ = 5000 - QUEUED
- **Status**: Pending

### ⏳ Annealed EWC - QUEUED
- **Status**: Pending (after sweep)

---

## Phase Transition Curve

| λ | Final Task | Drop | Total Drop |
|---|------------|------|------------|
| 0 | 73.30% | - | - |
| 200 | 66.70% | -6.60% | -6.60% |
| 500 | 63.30% | -3.40% | -10.00% |
| 1000 | [running...] | [~-3%] | [~-13%] |

**Trend**: Monotonic degradation continues ✓

---

**Status**: 3/6 λ values complete, λ=1000 running (~40 min)
