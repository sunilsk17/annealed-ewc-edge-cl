# ResNet-18 CIFAR-100 Progress Tracker

## Experiment Status: RUNNING

**Architecture**: ResNet-18 (11.2M parameters)  
**Dataset**: CIFAR-100 (10 tasks, 10 classes each)  
**Start Time**: 2026-01-30 17:27 IST  
**Estimated Duration**: 4-5 hours

---

## Progress

### 🔄 λ = 0 (Baseline) - RUNNING
- **Status**: Starting...
- **Expected**: ~35-40 minutes (10 tasks, 10 epochs each)

### ⏳ λ = 200 - QUEUED
### ⏳ λ = 500 - QUEUED
### ⏳ λ = 1000 - QUEUED
### ⏳ λ = 2000 - QUEUED
### ⏳ λ = 5000 - QUEUED
### ⏳ Annealed EWC - QUEUED

---

## Comparison Grid

|  | CIFAR-10 (5 tasks) | CIFAR-100 (10 tasks) |
|---|-------------------|---------------------|
| **MobileNetV3** | ✅ Complete | ✅ Complete |
| **ResNet-18** | ✅ Complete | 🔄 Running |

---

## Expected Completion

**Per λ value**: ~35-40 minutes  
**Total time**: 4-5 hours  
**ETA**: ~21:30-22:30 IST (9:30-10:30 PM)

---

**Monitor**: `tail -f resnet_cifar100_log.txt`  
**This completes the full 2×2 architecture×dataset grid!**
