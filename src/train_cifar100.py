"""
Training script for Split-CIFAR-100 with EWC

Supports:
- 10 sequential tasks (class-incremental)
- Configurable λ_EWC
- Checkpoint saving per task
"""

import torch
import torch.nn as nn
from torch.optim import Adam
import argparse
import os
import sys

# Import from existing modules
sys.path.append(os.path.dirname(__file__))
from data_cifar100 import SplitCIFAR100
from model import get_model, EWC

def train_cifar100(epochs=10, lambda_ewc=0, save_dir='checkpoints_cifar100'):
    """
    Train MobileNetV3 on Split-CIFAR-100 with EWC.
    
    Args:
        epochs: Epochs per task
        lambda_ewc: EWC penalty strength
        save_dir: Directory to save checkpoints
    """
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"Using device: {device}")
    print(f"Training Split-CIFAR-100: {10} tasks, {epochs} epochs/task, λ={lambda_ewc}")
    
    # Create save directory
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Load data
    split_cifar100 = SplitCIFAR100()
    task_loaders, test_loader = split_cifar100.get_loaders(batch_size=128)
    
    # Model (100 classes total for CIFAR-100)
    model = get_model(num_classes=100).to(device)
    optimizer = Adam(model.parameters(), lr=1e-3)
    
    ewc_modules = []
    
    for task_id, (train_loader, task_classes) in enumerate(task_loaders):
        print(f"\n{'='*60}")
        print(f"Training on Task {task_id} (Classes: {task_classes.tolist()})")
        print(f"{'='*60}")
        
        # Train this task
        for epoch in range(epochs):
            model.train()
            total_loss = 0
            correct = 0
            total = 0
            
            criterion = nn.CrossEntropyLoss()
            
            for x, y in train_loader:
                x, y = x.to(device), y.to(device)
                optimizer.zero_grad()
                
                output = model(x)
                ce_loss = criterion(output, y)
                
                # EWC penalty
                ewc_loss = 0
                if ewc_modules:
                    for ewc in ewc_modules:
                        ewc_loss += ewc.penalty(model)
                
                loss = ce_loss + ewc_loss
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
                pred = output.argmax(dim=1)
                correct += (pred == y).sum().item()
                total += y.size(0)
            
            acc = correct / total
            avg_loss = total_loss / len(train_loader)
            print(f"Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f} - Acc: {acc:.4f}")
        
        # Save checkpoint
        checkpoint_path = os.path.join(save_dir, f"model_task{task_id}.pt")
        torch.save(model.state_dict(), checkpoint_path)
        print(f"Saved: {checkpoint_path}")
        
        # Compute Fisher for this task (if using EWC)
        if lambda_ewc > 0:
            print(f"Computing Fisher for Task {task_id}...")
            ewc = EWC(model, train_loader, device, lambda_ewc=lambda_ewc)
            ewc_modules.append(ewc)
    
    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=10, help='Epochs per task')
    parser.add_argument('--lambda_ewc', type=float, default=0, help='EWC penalty')
    parser.add_argument('--save_dir', type=str, default='checkpoints_cifar100', 
                       help='Checkpoint directory')
    args = parser.parse_args()
    
    train_cifar100(
        epochs=args.epochs,
        lambda_ewc=args.lambda_ewc,
        save_dir=args.save_dir
    )
