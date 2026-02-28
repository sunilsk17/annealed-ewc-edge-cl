#!/bin/bash
# Run the full Drift EWC experiment
set -e

# Activate venv
source venv/bin/activate

# 1. Train
echo "Starting Training (5 tasks)..."
# Using 5 epochs per task as default. Adjust as needed.
python src/train.py --epochs 5 --save_dir checkpoints

# 2. Export
echo "Exporting to TFLite..."
# Assumes export.py looks for checkpoints/model_task4.pt
python src/export.py

# 3. Eval
echo "Running TFLite Evaluation..."
python src/eval.py

# 4. Analysis
echo "Generating PAC-Bayes Analysis..."
python src/analysis.py

echo "Experiment Complete. Results saved to drift_curve.png"
