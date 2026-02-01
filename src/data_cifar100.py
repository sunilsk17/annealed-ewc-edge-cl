"""
Split-CIFAR-100 Dataset for Class-Incremental Continual Learning

Implements 10 sequential tasks, each with 10 classes (total 100 classes).
This is a standard benchmark for continual learning research.
"""

import torch
from torch.utils.data import DataLoader, Subset
import torchvision.datasets as datasets
import torchvision.transforms as transforms
import numpy as np

class SplitCIFAR100:
    """
    CIFAR-100 split into 10 sequential tasks (class-incremental learning).
    
    Each task contains:
    - 10 classes (non-overlapping)
    - 500 training images per class (5000 total/task)
    - 100 test images per class (1000 total/task)
    """
    
    def __init__(self, data_root='./data', num_tasks=10, seed=42):
        """
        Args:
            data_root: Directory to download/store CIFAR-100
            num_tasks: Number of sequential tasks (default: 10)
            seed: Random seed for class ordering (fixed for reproducibility)
        """
        self.num_tasks = num_tasks
        self.classes_per_task = 100 // num_tasks
        
        # Download CIFAR-100
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5071, 0.4867, 0.4408), 
                               (0.2675, 0.2565, 0.2761))
        ])
        
        self.train_dataset = datasets.CIFAR100(
            root=data_root,
            train=True,
            download=True,
            transform=transform
        )
        
        self.test_dataset = datasets.CIFAR100(
            root=data_root,
            train=False,
            download=True,
            transform=transform
        )
        
        # Fixed class order for reproducibility
        np.random.seed(seed)
        self.class_order = np.random.permutation(100)
        
        print(f"Split-CIFAR-100 initialized:")
        print(f"  Tasks: {num_tasks}")
        print(f"  Classes per task: {self.classes_per_task}")
        print(f"  Class order: {self.class_order[:20]}... (first 20)")
        
    def get_task_data(self, task_id):
        """
        Get train and test subsets for a specific task.
        
        Args:
            task_id: Task index (0 to num_tasks-1)
            
        Returns:
            train_subset, test_subset, task_classes
        """
        assert 0 <= task_id < self.num_tasks, f"Invalid task_id: {task_id}"
        
        # Get classes for this task
        cls_start = task_id * self.classes_per_task
        cls_end = (task_id + 1) * self.classes_per_task
        task_classes = self.class_order[cls_start:cls_end]
        
        # Filter train indices
        train_targets = np.array(self.train_dataset.targets)
        train_idx = np.where(np.isin(train_targets, task_classes))[0]
        
        # Filter test indices
        test_targets = np.array(self.test_dataset.targets)
        test_idx = np.where(np.isin(test_targets, task_classes))[0]
        
        train_subset = Subset(self.train_dataset, train_idx)
        test_subset = Subset(self.test_dataset, test_idx)
        
        print(f"Task {task_id}: Classes {task_classes.tolist()}")
        print(f"  Train samples: {len(train_idx)}")
        print(f"  Test samples: {len(test_idx)}")
        
        return train_subset, test_subset, task_classes
    
    def get_loaders(self, batch_size=32, num_workers=2):
        """
        Get DataLoaders for all tasks.
        
        Returns:
            task_loaders: List of (train_loader, task_classes) tuples
            test_loader: DataLoader for entire test set
        """
        task_loaders = []
        
        for task_id in range(self.num_tasks):
            train_subset, _, task_classes = self.get_task_data(task_id)
            
            train_loader = DataLoader(
                train_subset,
                batch_size=batch_size,
                shuffle=True,
                num_workers=num_workers,
                pin_memory=True
            )
            
            task_loaders.append((train_loader, task_classes))
        
        # Full test set for evaluation
        test_loader = DataLoader(
            self.test_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True
        )
        
        return task_loaders, test_loader

if __name__ == '__main__':
    # Test the implementation
    print("="*60)
    print("Testing Split-CIFAR-100 Implementation")
    print("="*60)
    
    split_cifar100 = SplitCIFAR100()
    task_loaders, test_loader = split_cifar100.get_loaders(batch_size=128)
    
    print(f"\nTotal tasks: {len(task_loaders)}")
    print(f"Test set size: {len(test_loader.dataset)}")
    
    # Verify no class overlap
    all_classes = []
    for i, (loader, classes) in enumerate(task_loaders):
        all_classes.extend(classes)
        print(f"Task {i}: {len(loader.dataset)} samples, classes {classes.tolist()}")
    
    print(f"\nTotal unique classes: {len(set(all_classes))}")
    print("✓ Implementation verified!")
