# ResNet-18 Experiments Quick Start Guide

## Overview

Run ResNet-18 (11.2M params) on both CIFAR-10 and CIFAR-100 to validate findings across architectures.

---

## One-Command Execution

### Option 1: Run Both Datasets Sequentially (~9-11 hours total)

```bash
caffeinate -d -i -s -t 40000 &  # Keep awake for 11 hours
./run_resnet_cifar10_all.sh && ./run_resnet_cifar100_all.sh
```

### Option 2: Run CIFAR-10 Only (~3-4 hours)

```bash
caffeinate -d -i -s -t 15000 &  # Keep awake for 4 hours
./run_resnet_cifar10_all.sh
```

### Option 3: Run CIFAR-100 Only (~4-5 hours)

```bash
caffeinate -d -i -s -t 18000 &  # Keep awake for 5 hours
./run_resnet_cifar100_all.sh
```

---

## What Gets Created

### CIFAR-10 Results
```
results_resnet_cifar10/
├── lambda_sweep/
│   ├── lambda_0_results.json
│   ├── lambda_200_results.json
│   ├── lambda_500_results.json
│   ├── lambda_1000_results.json
│   ├── lambda_2000_results.json
│   ├── lambda_5000_results.json
│   └── sweep_results.json (aggregated)
└── annealed_ewc/
    └── annealed_results.json
```

### CIFAR-100 Results
```
results_resnet_cifar100/
├── lambda_sweep/
│   ├── lambda_0_results.json
│   ├── lambda_200_results.json
│   ├── lambda_500_results.json
│   ├── lambda_1000_results.json
│   ├── lambda_2000_results.json
│   ├── lambda_5000_results.json
│   └── sweep_results.json (aggregated)
└── annealed_ewc/
    └── annealed_results.json
```

---

## Expected Results

Based on MobileNetV3 pattern, we expect:
- **Monotonic degradation** with increasing λ
- **~20-25% total drop** from λ=0 to λ=5000
- **Similar pattern** to MobileNetV3 (validates architecture independence)

---

## Time Estimates (M2 MacBook Air)

| Experiment | Tasks | Estimated Time |
|-----------|-------|----------------|
| ResNet C10 λ=0 | 5 | ~25-30 min |
| ResNet C10 each λ | 5 | ~25-30 min |
| ResNet C10 total | - | ~3-4 hours |
| ResNet C100 λ=0 | 10 | ~45-50 min |
| ResNet C100 each λ | 10 | ~45-50 min |
| ResNet C100 total | - | ~4-5 hours |

**Both datasets: ~9-11 hours total**

---

## Monitoring Progress

Check training logs in real-time:
```bash
tail -f resnet_cifar10_log.txt
# or
tail -f resnet_cifar100_log.txt
```

---

## After Completion

Compare architectures:
- MobileNetV3 (310k params) vs ResNet-18 (11.2M params)
- Shows findings generalize across 36× parameter range
- Strengthens Q1 journal submission significantly

---

**Ready to run? Just copy one of the commands above!**
