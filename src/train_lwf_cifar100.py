"""
Learning without Forgetting (LwF) for MobileNetV3 on CIFAR-100

Key differences from EWC:
- Uses knowledge distillation instead of parameter regularization
- Teacher model frozen from previous task
- Distillation on new task data (no need for old data)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import Adam
import argparse
import os
import sys
import copy

sys.path.append(os.path.dirname(__file__))
from data_cifar100 import SplitCIFAR100
from model import get_model

def distillation_loss(student_logits, teacher_logits, T=2):
    """
    Knowledge Distillation loss with temperature scaling
    
    Args:
        student_logits: Predictions from current model
        teacher_logits: Predictions from frozen previous model
        T: Temperature for softening probabilities (default 2)
    
    Returns:
        KL divergence loss scaled by T^2
    """
    soft_student = F.log_softmax(student_logits / T, dim=1)
    soft_teacher = F.softmax(teacher_logits / T, dim=1)
    
    # KL divergence
    kl_loss = F.kl_div(soft_student, soft_teacher, reduction='batchmean')
    
    # Scale by T^2 as per Hinton et al.
    return kl_loss * (T ** 2)

def train_lwf_cifar100(epochs=10, lambda_distill=1.0, T=2, save_dir='checkpoints_lwf_cifar100'):
    """
    Train MobileNetV3 on Split-CIFAR-100 with Learning without Forgetting
    
    Args:
        epochs: Epochs per task
        lambda_distill: Weight for distillation loss
        T: Temperature for distillation
        save_dir: Directory to save checkpoints
    """
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"Using device: {device}")
    print(f"Training MobileNetV3 on Split-CIFAR-100 with LwF")
    print(f"λ_distill={lambda_distill}, Temperature={T}")
    
    # Create save directory
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Load data
    split_cifar100 = SplitCIFAR100()
    task_loaders, test_loader = split_cifar100.get_loaders(batch_size=128)
    
    # Model
    model = get_model(num_classes=100).to(device)
    optimizer = Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()
    
    # Teacher model (will be updated after each task)
    teacher_model = None
    
    for task_id, (train_loader, task_classes) in enumerate(task_loaders):
        num_old_classes = task_id * 10  # Classes seen before this task
        
        print(f"\n{'='*60}")
        print(f"Training on Task {task_id} (Classes: {task_classes.tolist()})")
        if teacher_model is not None:
            print(f"Using distillation on {num_old_classes} old classes")
        print(f"{'='*60}")
        
        # Train this task
        for epoch in range(epochs):
            model.train()
            total_loss = 0
            total_ce_loss = 0
            total_distill_loss = 0
            correct = 0
            total = 0
            
            for x, y in train_loader:
                x, y = x.to(device), y.to(device)
                optimizer.zero_grad()
                
                # Forward pass
                outputs = model(x)
                
                # Cross-entropy loss on new task
                ce_loss = criterion(outputs, y)
                
                # Distillation loss (if not first task)
                distill_loss_val = 0
                if teacher_model is not None:
                    with torch.no_grad():
                        teacher_outputs = teacher_model(x)
                    
                    # Distill only on old classes
                    if num_old_classes > 0:
                        distill_loss_val = distillation_loss(
                            outputs[:, :num_old_classes],
                            teacher_outputs[:, :num_old_classes],
                            T=T
                        )
                
                # Total loss
                loss = ce_loss + lambda_distill * distill_loss_val
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
                total_ce_loss += ce_loss.item()
                if isinstance(distill_loss_val, torch.Tensor):
                    total_distill_loss += distill_loss_val.item()
                
                pred = outputs.argmax(dim=1)
                correct += (pred == y).sum().item()
                total += y.size(0)
            
            acc = correct / total
            avg_loss = total_loss / len(train_loader)
            avg_ce = total_ce_loss / len(train_loader)
            avg_distill = total_distill_loss / len(train_loader) if teacher_model else 0
            
            print(f"Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f} "
                  f"(CE: {avg_ce:.4f}, Distill: {avg_distill:.4f}) - Acc: {acc:.4f}")
        
        # Save checkpoint
        checkpoint_path = os.path.join(save_dir, f"model_task{task_id}.pt")
        torch.save(model.state_dict(), checkpoint_path)
        print(f"Saved: {checkpoint_path}")
        
        # Update teacher model for next task
        teacher_model = copy.deepcopy(model)
        teacher_model.eval()
        for param in teacher_model.parameters():
            param.requires_grad = False
        print(f"Teacher model updated (frozen)")
    
    print("\n" + "="*60)
    print("LwF Training Complete!")
    print(f"λ_distill={lambda_distill}, Temperature={T}")
    print("="*60)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=10, help='Epochs per task')
    parser.add_argument('--lambda_distill', type=float, default=1.0, 
                       help='Distillation loss weight')
    parser.add_argument('--temperature', type=float, default=2.0,
                       help='Distillation temperature')
    parser.add_argument('--save_dir', type=str, default='checkpoints_lwf_cifar100',
                       help='Checkpoint directory')
    args = parser.parse_args()
    
    train_lwf_cifar100(
        epochs=args.epochs,
        lambda_distill=args.lambda_distill,
        T=args.temperature,
        save_dir=args.save_dir
    )
