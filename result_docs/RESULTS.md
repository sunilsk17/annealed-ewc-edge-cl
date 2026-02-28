# Experimental Results

All results are from 15 epochs/task, Adam lr=1e-3, MobileNetV3-Small (~310K params) unless noted.
Accuracy values are from evaluation on each drift environment's training subset after all tasks are trained.

---

## CIFAR-10 Sequential Drift — λ Sweep (MobileNetV3-Small)

5 environments: Clean → Fog (gamma) → Night (low brightness) → Snow (whitewash) → Blur (gaussian)

| λ | Env 0 | Env 1 | Env 2 | Env 3 | Env 4 (Final) | Early Avg | Final Avg |
|---|-------|-------|-------|-------|----------------|-----------|-----------|
| 0 (no EWC) | 17.34% | 17.54% | 18.18% | 17.30% | **58.24%** | 17.59% | 25.72% |
| 200 | 20.30% | 17.16% | 18.92% | 17.20% | **51.64%** | 18.40% | 25.04% |
| 500 | 13.76% | 13.88% | 15.36% | 13.38% | **49.20%** | 14.09% | 21.12% |
| 1000 | 13.86% | 13.72% | 14.84% | 12.60% | **47.52%** | 13.76% | 20.51% |
| 2000 | 16.12% | 15.60% | 17.42% | 15.00% | **46.38%** | 16.04% | 22.10% |
| 5000 | 12.22% | 13.48% | 13.34% | 12.44% | **44.30%** | 12.87% | 19.16% |
| Annealed (λ₀=5000) | 22.40% | 24.46% | 23.68% | 20.82% | **48.02%** | **22.84%** | **27.88%** |

**Early Avg** = mean accuracy on environments 0–3 after all training.  
**Final Avg** = mean accuracy across all 5 environments.

---

## CIFAR-100 Class-Incremental — λ Sweep (MobileNetV3-Small)

10 tasks, 10 classes each (100 total classes).

| λ | Final Task Acc | Early Avg | AIA |
|---|---------------|-----------|-----|
| 0 (no EWC) | 73.30% | ~0.02% | 7.35% |
| 200 | 66.70% | ~0.07% | 6.73% |
| 500 | 63.30% | ~0.11% | 6.43% |
| 1000 | 62.60% | ~0.30% | 6.53% |
| 2000 | 59.80% | ~0.19% | 6.15% |
| 5000 | 55.70% | 0.43% | 5.96% |
| Annealed (λ₀=5000) | 63.10% | ~0.03% | 6.34% |

**AIA** = Average Incremental Accuracy across all seen tasks at each step.

---

## LwF on CIFAR-100 (MobileNetV3-Small)

| Metric | Value |
|--------|-------|
| AIA | **8.48%** |
| Final task accuracy | 10.65% |
| Early tasks avg | 8.24% |
| Forgetting | 91.76% |

---

## Architecture Comparison — CIFAR-10 Drift (λ Sweep)

| λ | MobileNetV3 (310K) | ResNet-18 (11.7M) |
|---|--------------------|--------------------|
| 0 | 58.24% | 72.80% |
| 100 | 54.10% | 58.20% |
| 500 | 50.25% | 65.15% |
| 1000 | 47.80% | 69.90% |
| 5000 | 44.30% | 61.40% |
| Optimization curve | Monotonic collapse ↓ | Non-monotonic (U-shaped) |

---

## ResNet-18 CIFAR-100 — Class-Incremental (Selected)

| λ | Final Task Acc | AIA |
|---|---------------|-----|
| 0 | ~70% | ~8% |
| 5000 | ~55% | ~7% |
| Annealed | ~62% | ~8% |

*(ResNet-18 CIFAR-100 results stored in `results_resnet_cifar100/`)*

---

## Raw Data Files

| File | Contents |
|------|----------|
| `ALL_RESULTS_CONSOLIDATED.json` | All MobileNetV3 results (CIFAR-10 + CIFAR-100) |
| `lwf_test_results.json` | LwF per-task accuracy matrix |
| `results/lambda_sweep/` | Per-λ checkpoint eval JSONs (CIFAR-10, MobileNetV3) |
| `results_cifar100/` | CIFAR-100 MobileNetV3 results |
| `results_resnet_cifar10/` | ResNet-18 CIFAR-10 results |
| `results_resnet_cifar100/` | ResNet-18 CIFAR-100 results |
