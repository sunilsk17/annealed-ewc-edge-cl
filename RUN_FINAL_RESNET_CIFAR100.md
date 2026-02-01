# How to Complete ResNet-18 CIFAR-100 Experiments

## Time Estimate

**Total time**: 2-2.5 hours  
**Start**: 22:10 IST  
**Expected completion**: 00:30-01:00 IST (12:30-1:00 AM)

**Breakdown**:
- λ=2000: ~45 minutes
- λ=5000: ~45 minutes  
- Annealed EWC: ~45 minutes
- Evaluation: ~5 minutes total

---

## ONE COMMAND TO RUN EVERYTHING

Copy and paste this into your terminal:

```bash
cd "/Users/sunilkumars/Desktop/EWC Project/drift_cl_edge" && \
caffeinate -d -i -s bash finish_resnet_cifar100.sh 2>&1 | tee resnet_cifar100_final_log.txt
```

**What this does**:
- `caffeinate`: Keeps Mac awake for entire duration
- `-d`: Prevents display sleep
- `-i`: Prevents system idle sleep
- `-s`: Prevents system sleep
- `tee`: Saves output to log file while showing on screen

---

## What Gets Run

1. **Clean up** incomplete λ=2000
2. **Train & evaluate** λ=2000 (10 tasks, 10 epochs each)
3. **Train & evaluate** λ=5000 (10 tasks, 10 epochs each)
4. **Train & evaluate** Annealed EWC (10 tasks, adaptive λ)

---

## Output Files

After completion, you'll have:

### Results:
- `results_resnet_cifar100/lambda_sweep/lambda_2000_results.json`
- `results_resnet_cifar100/lambda_sweep/lambda_5000_results.json`
- `results_resnet_cifar100/annealed_ewc/annealed_results.json`

### Log:
- `resnet_cifar100_final_log.txt` (full output)

### Checkpoints:
- `results_resnet_cifar100/lambda_sweep/lambda_2000/` (10 checkpoints)
- `results_resnet_cifar100/lambda_sweep/lambda_5000/` (10 checkpoints)
- `checkpoints_resnet_cifar100_annealed/` (10 checkpoints)

---

## Monitoring Progress

**In another terminal**, check progress:
```bash
tail -f resnet_cifar100_final_log.txt
```

You'll see:
- Current task being trained
- Epoch progress (1/10 through 10/10)
- Accuracy improving each epoch

---

## If Something Goes Wrong

**Memory issues again?**
- The script will stop at that point
- Check log: `tail -100 resnet_cifar100_final_log.txt`
- Completed experiments are saved
- Can resume from where it stopped

**Want to stop manually?**
- Press `Ctrl+C` in the terminal
- Already completed experiments are saved

---

## After Completion

You'll have:
- ✅ Complete 2×2 grid: MobileNetV3 + ResNet-18 × CIFAR-10 + CIFAR-100
- ✅ All λ values (0, 200, 500, 1000, 2000, 5000)
- ✅ Annealed EWC for all combinations
- ✅ Publication-ready results!

---

**Ready? Copy the command above and run it!** 🚀
