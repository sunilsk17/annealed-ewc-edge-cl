"""
ResNet-18 Annealed EWC Training for CIFAR-100

10 sequential tasks, 10 classes per task
Implements adaptive λ decay: λ_t = λ_0 / (1 + t)
"""

import torch
import torch.nn as nn
from torch.optim import Adam
import argparse
import os
import sys

sys.path.append(os.path.dirname(__file__))
from data_cifar100 import SplitCIFAR100
from model_resnet import get_resnet18_cifar
from model import EWC

def train_resnet_cifar100_annealed(epochs=10, lambda_0=5000, save_dir='checkpoints_resnet_cifar100_annealed'):
    """
    Train ResNet-18 on Split-CIFAR-100 with Annealed EWC.
    
    Args:
        epochs: Epochs per task
        lambda_0: Initial EWC penalty strength
        save_dir: Directory to save checkpoints
    """
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"Using device: {device}")
    print(f"Training ResNet-18 on Split-CIFAR-100 with Annealed EWC")
    print(f"λ schedule: λ_t = {lambda_0}/(1+t)")
    
    # Create save directory
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Load data
    split_cifar100 = SplitCIFAR100()
    task_loaders, test_loader = split_cifar100.get_loaders(batch_size=128)
    
    # Model (ResNet-18 for CIFAR-100)
    model = get_resnet18_cifar(num_classes=100).to(device)
    optimizer = Adam(model.parameters(), lr=1e-3)
    
    ewc_modules = []
    
    for task_id, (train_loader, task_classes) in enumerate(task_loaders):
        # Compute annealed lambda for this task
        lambda_t = lambda_0 / (1 + task_id)
        
        print(f"\n{'='*60}")
        print(f"Training on Task {task_id} (Classes: {task_classes.tolist()}, λ={lambda_t:.1f})")
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
        
        # Compute Fisher for this task (with current annealed λ)
        print(f"Computing Fisher for Task {task_id} (λ={lambda_t:.1f})...")
        ewc = EWC(model, train_loader, device, lambda_ewc=lambda_t)
        ewc_modules.append(ewc)
    
    print("\n" + "="*60)
    print("Annealed EWC Training Complete!")
    print(f"λ schedule used: {[f'{lambda_0/(1+t):.1f}' for t in range(len(task_loaders))]}")
    print("="*60)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=10, help='Epochs per task')
    parser.add_argument('--lambda_0', type=float, default=5000, help='Initial EWC penalty')
    parser.add_argument('--save_dir', type=str, default='checkpoints_resnet_cifar100_annealed', 
                       help='Checkpoint directory')
    args = parser.parse_args()
    
    train_resnet_cifar100_annealed(
        epochs=args.epochs,
        lambda_0=args.lambda_0,
        save_dir=args.save_dir
    )
