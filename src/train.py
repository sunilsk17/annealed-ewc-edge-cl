import torch
import torch.nn as nn
from torch.optim import Adam
import os
import argparse
from data import DriftCIFAR10
from model import get_model, EWC

def train_one_epoch(model, loader, optimizer, ewc_modules, device):
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
        
        ewc_loss = 0
        if ewc_modules:
            ewc_loss = sum([ewc.penalty(model) for ewc in ewc_modules])
            
        loss = ce_loss + ewc_loss
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        pred = output.argmax(dim=1)
        correct += (pred == y).sum().item()
        total += y.size(0)
        
    return total_loss / len(loader), correct / total

def evaluate(model, loader, device):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            output = model(x)
            pred = output.argmax(dim=1)
            correct += (pred == y).sum().item()
            total += y.size(0)
    return correct / total

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=5, help='Epochs per task')
    parser.add_argument('--lr', type=float, default=1e-3)
    parser.add_argument('--lambda_ewc', type=float, default=1000)
    parser.add_argument('--save_dir', type=str, default='checkpoints')
    args = parser.parse_args()
    
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    if not os.path.exists(args.save_dir):
        os.makedirs(args.save_dir)
        
    # Data
    drift_data = DriftCIFAR10()
    task_loaders, test_loader = drift_data.get_loaders()
    
    # Model
    model = get_model(num_classes=10).to(device)
    optimizer = Adam(model.parameters(), lr=args.lr)
    
    ewc_modules = []
    
    # Store accuracies
    accuracies = []
    
    for task_id, loader in enumerate(task_loaders):
        print(f"\nTraining on Task {task_id} (Env {task_id})")
        
        # Train
        for epoch in range(args.epochs):
            loss, acc = train_one_epoch(model, loader, optimizer, ewc_modules, device)
            print(f"Epoch {epoch+1}/{args.epochs} - Loss: {loss:.4f} - Acc: {acc:.4f}")
            
        # Evaluate on current task (or all? Usually we care about forgeting, so eval on all seen tasks? User script evaluates on drifting envs).
        # We'll save the model.
        torch.save(model.state_dict(), os.path.join(args.save_dir, f"model_task{task_id}.pt"))
        
        # Calculate EWC for this task and add to modules
        print(f"Computing Fisher for Task {task_id}...")
        ewc = EWC(model, loader, device, lambda_ewc=args.lambda_ewc)
        ewc_modules.append(ewc)
        
    print("Training Complete.")

if __name__ == '__main__':
    main()
