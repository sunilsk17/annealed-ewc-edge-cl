"""
Annealed EWC Implementation

Key innovation: Dynamic λ decay that allows early task protection while
maintaining plasticity for later tasks.

λ_t = λ_0 / (1 + task_id)  or  λ_0 * exp(-α * task_id)

This prevents catastrophic rigidity while retaining EWC benefits.
"""

import torch
import torch.nn as nn
from model import get_model, EWC
from data import DriftCIFAR10
from torch.optim import Adam
import os
import argparse

def train_annealed_ewc(lambda_0=5000, decay_type='inverse', alpha=0.5, epochs=15, save_dir='checkpoints_annealed'):
    """
    Train with annealed (decaying) λ_EWC.
    
    Args:
        lambda_0: Initial λ value
        decay_type: 'inverse' (1/(1+t)) or 'exponential' (exp(-α*t))
        alpha: Decay rate for exponential
        epochs: Epochs per task
        save_dir: Directory to save checkpoints
    """
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"Using device: {device}")
    print(f"Annealed EWC: λ_0={lambda_0}, decay={decay_type}, α={alpha}")
    
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Data
    drift_data = DriftCIFAR10()
    task_loaders, test_loader = drift_data.get_loaders()
    
    # Model
    model = get_model(num_classes=10).to(device)
    optimizer = Adam(model.parameters(), lr=1e-3)
    
    ewc_modules = []
    lambda_schedule = []
    
    for task_id, loader in enumerate(task_loaders):
        # Calculate current lambda
        if decay_type == 'inverse':
            lambda_t = lambda_0 / (1 + task_id)
        elif decay_type == 'exponential':
            lambda_t = lambda_0 * torch.exp(torch.tensor(-alpha * task_id)).item()
        else:
            lambda_t = lambda_0
        
        lambda_schedule.append(lambda_t)
        
        print(f"\n{'='*60}")
        print(f"Training on Task {task_id} (Env {task_id}) - λ_t = {lambda_t:.2f}")
        print(f"{'='*60}")
        
        # Train
        for epoch in range(epochs):
            model.train()
            total_loss = 0
            correct = 0
            total = 0
            
            criterion = nn.CrossEntropyLoss()
            
            for x, y in loader:
                x, y = x.to(device), y.to(device)
                optimizer.zero_grad()
                
                output = model(x)
                ce_loss = criterion(output, y)
                
                # EWC penalty with current lambda
                ewc_loss = 0
                if ewc_modules:
                    for ewc in ewc_modules:
                        ewc_loss += ewc.penalty(model) * (lambda_t / ewc.lambda_ewc)  # Scale by current/original ratio
                
                loss = ce_loss + ewc_loss
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
                pred = output.argmax(dim=1)
                correct += (pred == y).sum().item()
                total += y.size(0)
            
            acc = correct / total
            print(f"Epoch {epoch+1}/{epochs} - Loss: {total_loss/len(loader):.4f} - Acc: {acc:.4f}")
        
        # Save checkpoint
        torch.save(model.state_dict(), os.path.join(save_dir, f"model_task{task_id}.pt"))
        
        # Compute Fisher for this task (using original lambda_0 for storage)
        print(f"Computing Fisher for Task {task_id}...")
        ewc = EWC(model, loader, device, lambda_ewc=lambda_0)
        ewc_modules.append(ewc)
    
    print("\nTraining Complete.")
    print(f"Lambda schedule used: {lambda_schedule}")
    
    # Save lambda schedule
    import json
    with open(os.path.join(save_dir, 'lambda_schedule.json'), 'w') as f:
        json.dump({'lambda_0': lambda_0, 'decay_type': decay_type, 'alpha': alpha, 
                   'schedule': lambda_schedule}, f, indent=2)
    
    return lambda_schedule

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--lambda_0', type=float, default=5000, help='Initial lambda')
    parser.add_argument('--decay_type', type=str, default='inverse', choices=['inverse', 'exponential', 'none'])
    parser.add_argument('--alpha', type=float, default=0.5, help='Exponential decay rate')
    parser.add_argument('--epochs', type=int, default=15, help='Epochs per task')
    parser.add_argument('--save_dir', type=str, default='checkpoints_annealed')
    args = parser.parse_args()
    
    train_annealed_ewc(
        lambda_0=args.lambda_0,
        decay_type=args.decay_type,
        alpha=args.alpha,
        epochs=args.epochs,
        save_dir=args.save_dir
    )
