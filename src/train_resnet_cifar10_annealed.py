"""
ResNet-18 Annealed EWC Training for CIFAR-10

Implements adaptive λ decay: λ_t = λ_0 / (1 + t)
"""

import torch
import torch.nn as nn
from torch.optim import Adam
import argparse
import os
import sys

sys.path.append(os.path.dirname(__file__))
from data import DriftCIFAR10
from model_resnet import get_resnet18_cifar
from model import EWC

def train_resnet_cifar10_annealed(epochs=10, lambda_0=5000, save_dir='checkpoints_resnet_cifar10_annealed'):
    """
    Train ResNet-18 on CIFAR-10 drift environments with Annealed EWC.
    
    Args:
        epochs: Epochs per environment
        lambda_0: Initial EWC penalty strength
        save_dir: Directory to save checkpoints
    """
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"Using device: {device}")
    print(f"Training ResNet-18 on CIFAR-10 with Annealed EWC")
    print(f"λ schedule: λ_t = {lambda_0}/(1+t)")
    
    # Create save directory
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Load drift environments
    drift_data = DriftCIFAR10(batch_size=128)
    task_loaders, test_loader = drift_data.get_loaders()
    
    # Model (ResNet-18 for CIFAR-10)
    model = get_resnet18_cifar(num_classes=10).to(device)
    optimizer = Adam(model.parameters(), lr=1e-3)
    
    ewc_modules = []
    
    for task_id, train_loader in enumerate(task_loaders):
        # Compute annealed lambda for this task
        lambda_t = lambda_0 / (1 + task_id)
        
        print(f"\n{'='*60}")
        print(f"Training on Environment {task_id} (λ={lambda_t:.1f})")
        print(f"{'='*60}")
        
        # Train this environment
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
        
        # Compute Fisher for this environment (with current annealed λ)
        print(f"Computing Fisher for Environment {task_id} (λ={lambda_t:.1f})...")
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
    parser.add_argument('--save_dir', type=str, default='checkpoints_resnet_cifar10_annealed', 
                       help='Checkpoint directory')
    args = parser.parse_args()
    
    train_resnet_cifar10_annealed(
        epochs=args.epochs,
        lambda_0=args.lambda_0,
        save_dir=args.save_dir
    )
