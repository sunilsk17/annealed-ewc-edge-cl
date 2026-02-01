# Resume Script for ResNet-18 CIFAR-100

**Issue**: Training stopped on λ=2000 due to memory issue

**What was completed**: λ=0, 200, 500, 1000  
**What stopped**: λ=2000 (Task 9, Epoch 8/10 - incomplete)  
**What remains**: Complete λ=2000, then λ=5000, Annealed

---

## Resume Strategy

### Option 1: Restart λ=2000 from scratch (~45 min)
```bash
# Delete incomplete λ=2000
rm -rf results_resnet_cifar100/lambda_sweep/lambda_2000*

# Run remaining experiments
cd "/Users/sunilkumars/Desktop/EWC Project/drift_cl_edge"
source venv/bin/activate

# λ=2000
python src/train_resnet_cifar100.py --epochs 10 --lambda_ewc 2000 --save_dir results_resnet_cifar100/lambda_sweep/lambda_2000
python src/eval_resnet_cifar100.py --checkpoint results_resnet_cifar100/lambda_sweep/lambda_2000/model_task9.pt --output results_resnet_cifar100/lambda_sweep/lambda_2000_results.json

# λ=5000
python src/train_resnet_cifar100.py --epochs 10 --lambda_ewc 5000 --save_dir results_resnet_cifar100/lambda_sweep/lambda_5000
python src/eval_resnet_cifar100.py --checkpoint results_resnet_cifar100/lambda_sweep/lambda_5000/model_task9.pt --output results_resnet_cifar100/lambda_sweep/lambda_5000_results.json

# Annealed
python src/train_resnet_cifar100_annealed.py --lambda_0 5000 --epochs 10 --save_dir checkpoints_resnet_cifar100_annealed
python src/eval_resnet_cifar100.py --checkpoint checkpoints_resnet_cifar100_annealed/model_task9.pt --output results_resnet_cifar100/annealed_ewc/annealed_results.json
```

### Option 2: Skip λ=2000 and λ=5000, just run Annealed (~45 min)
Since we have λ=0, 200, 500, 1000, we have enough for analysis.

---

**Recommendation**: Run remaining experiments individually with caffeinate to prevent sleep/memory issues.
