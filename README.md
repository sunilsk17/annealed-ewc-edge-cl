# Continual Learning under Edge Capacity Constraints

Experiments on Elastic Weight Consolidation (EWC) and its variants for continual learning with a lightweight MobileNetV3-Small model. The core investigation is how regularization-based continual learning methods behave under strict parameter constraints, and whether adaptive regularization schedules can help.

---

## What's in this repo

- **EWC with λ-sweep**: trained across λ ∈ {0, 200, 500, 1000, 2000, 5000} on sequential CIFAR-10 drift and class-incremental CIFAR-100
- **Annealed EWC**: harmonic decay schedule `λ_t = λ_0 / (1 + t)` to progressively relax the Fisher penalty
- **Learning without Forgetting (LwF)**: knowledge distillation baseline on CIFAR-100
- **Multi-architecture comparison**: same sweep on ResNet-18 to compare behaviour across model sizes

---

## Setup

```bash
pip install torch torchvision timm
```

---

## Running experiments

**CIFAR-10 λ-sweep (MobileNetV3):**
```bash
python run_lambda_sweep.py --epochs 15
```

**Annealed EWC (CIFAR-10):**
```bash
python src/train_annealed.py --lambda_0 5000 --decay_type inverse --epochs 15
```

**CIFAR-100 class-incremental sweep:**
```bash
python run_cifar100_sweep.py
```

**LwF on CIFAR-100:**
```bash
python src/train_lwf_cifar100.py --epochs 10 --lambda_distill 1.0
```

**ResNet-18 experiments:**
```bash
bash run_resnet_cifar10_all.sh
bash run_resnet_cifar100_all.sh
```

**Evaluate a trained checkpoint:**
```bash
python src/eval_pytorch.py --checkpoint results/lambda_sweep/lambda_0/model_task4.pt
```

**Reproduce paper plots:**
```bash
python generate_paper_plots.py
```

---

## Results

All results are stored as JSON files under `results/`, `results_cifar100/`, `results_resnet_cifar10/`, `results_resnet_cifar100/`.

The consolidated results are in `ALL_RESULTS_CONSOLIDATED.json`.

LwF results are in `lwf_test_results.json`.

---

## Source files

| File | Description |
|------|-------------|
| `src/model.py` | MobileNetV3-Small architecture + EWC class |
| `src/data.py` | CIFAR-10 drift environment data loader (5 environments) |
| `src/data_cifar100.py` | Split-CIFAR-100 class-incremental loader |
| `src/train.py` | Sequential EWC training |
| `src/train_annealed.py` | Annealed EWC training |
| `src/train_lwf_cifar100.py` | LwF training for CIFAR-100 |
| `src/train_resnet_cifar10.py` | ResNet-18 training on CIFAR-10 drift |
| `src/train_resnet_cifar100.py` | ResNet-18 training on CIFAR-100 |
| `src/eval_pytorch.py` | Evaluate a checkpoint across all drift environments |
| `src/eval_aia.py` | Average Incremental Accuracy evaluation for CIFAR-100 |
| `generate_paper_plots.py` | Generates all 3 paper figures |

---

## Experiment settings

| Setting | Value |
|---------|-------|
| Model | MobileNetV3-Small (~310K params) |
| CIFAR-10 setup | 5 sequential environments, 5000 samples each |
| Drift types | Clean → Fog (gamma) → Night (low brightness) → Snow (whitewash) → Blur (Gaussian) |
| CIFAR-100 setup | 10 tasks, 10 classes each (class-incremental) |
| Training | 15 epochs/task, Adam lr=1e-3 |
| Hardware | Apple Silicon (MPS) |
