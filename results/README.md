# Experimental Results

This folder contains raw experimental data (JSON files) and visualizations (PNG files).

## 📊 Structure

```
results/
├── lambda_sweep/              # λ-phase transition experiment
│   ├── *.json                 # Individual λ results
│   ├── sweep_results.json     # Aggregated data
│   └── *.png                  # Visualizations
│
├── annealed_ewc/              # Annealed EWC experiment
│   └── annealed_results.json
│
├── experiment_1_baseline/     # Initial experiments (5 epochs)
└── experiment_2_improved/     # Improved experiments (15 epochs)
```

## 📁 Key Files

### Lambda Sweep Results
- `lambda_sweep/sweep_results.json` - **Use this for analysis**
- `lambda_sweep/phase_transition.png` - Main figure for paper
- `lambda_sweep/pac_bayes_explanation.png` - Theory figure

### Individual Runs
- `lambda_0_results.json` through `lambda_5000_results.json`
- `annealed_ewc/annealed_results.json`

## 📖 Documentation

All analysis and writeups are in: `../result_docs/`

**For paper writing**: See `../result_docs/PAPER_READY_RESULTS.md`

---

**Data Format**: All JSON files contain `{"accuracies": [env0, env1, env2, env3, env4]}`  
**Plots**: Publication-ready 300 DPI PNG format
