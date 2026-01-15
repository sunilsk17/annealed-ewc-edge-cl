# EWC Experiment Results Summary

## Experiment 1: Baseline (5 epochs, 2k samples)
- **EWC (λ=1k)**: [11.8%, 13.4%, 12.1%, 12.0%, 42.7%]
- **Baseline (λ=0)**: [13.6%, 13.0%, 13.2%, 12.6%, 43.6%]
- **Gap**: ~1% (minimal difference)

## Experiment 2: Improved (15 epochs, 5k samples)
- **EWC (λ=5k)**: [11.6%, 11.2%, 12.2%, 12.0%, 44.6%]
- **Baseline (λ=0)**: [25.6%, 30.8%, 26.1%, 21.7%, 59.1%]
- **Gap**: 10-20% (Baseline better - EWC too restrictive)

## Key Finding
λ=5000 caused "catastrophic rigidity" - model couldn't learn new tasks.
For this problem scale (310k params), optimal λ likely in range 100-1000.

## Files
- experiment_1_baseline/: Initial results
- experiment_2_improved/: Improved training results
