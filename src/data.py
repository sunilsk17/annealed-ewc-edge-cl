import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Subset
import numpy as np
import os

def get_transforms():
    """Returns a list of transforms for the 5 environments."""
    # Env 0: Clean
    t0 = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    
    # Env 1: Fog (Simulated with Gamma correction for washing out)
    t1 = transforms.Compose([
        transforms.ToTensor(),
        transforms.Lambda(lambda x: transforms.functional.adjust_gamma(x, gamma=0.5)), # washed out
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    
    # Env 2: Night (Low brightness/contrast + Grayscale hint)
    # User's snippet had Grayscale(0.1) which is invalid. 
    # We use ColorJitter for brightness and slight desaturation.
    t2 = transforms.Compose([
        transforms.ColorJitter(brightness=0.2, contrast=0.5, saturation=0.5),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    
    # Env 3: Snow (Low saturation, high brightness/whitewash)
    t3 = transforms.Compose([
        transforms.ColorJitter(saturation=0.1, brightness=1.2),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    
    # Env 4: Blur (Gaussian Blur)
    # GaussianBlur is a class, so it works directly.
    t4 = transforms.Compose([
        transforms.ToTensor(),
        transforms.GaussianBlur(kernel_size=5, sigma=2.0),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    
    return [t0, t1, t2, t3, t4]

class DriftCIFAR10:
    def __init__(self, root='./data', download=True, batch_size=64):
        self.root = root
        self.batch_size = batch_size
        self.transforms_list = get_transforms()
        
        # We need the base dataset without transforms first, because we apply different transforms per subset
        # However, torchvision datasets apply transform at __getitem__.
        # We can wrap subsets to apply transform dynamically.
        
        self.train_data_base = datasets.CIFAR10(root=root, train=True, download=download)
        self.test_data_base = datasets.CIFAR10(root=root, train=False, download=download, transform=self.transforms_list[0]) # Test on clean? Or test on drifting? User script tests on all.
        
    def get_loaders(self):
        """Returns a list of (train_loader, test_loader) tuples for each environment."""
        loaders = []
        
        # 5 environments, 5000 images each (increased from 2000 for better learning)
        indices = np.random.permutation(len(self.train_data_base))
        # We can implement disjoint sets or sliding window. User snippet suggested simple chunking.
        
        for i, transform in enumerate(self.transforms_list):
            # Create a wrapper dataset that applies the specific transform
            # Subset just returns the item from the underlying dataset.
            # We need a custom Dataset class to override transform.
            
            # Slice 5000 indices
            start = i * 5000
            end = (i + 1) * 5000
            subset_indices = indices[start:end] # using random permutation for robustness, or user's np.arange for reproducibility? 
            # User used np.arange(i*5000...), which implies class imbalance is possible if data is ordered by class? 
            # CIFAR10 is usually shuffled? No, usually not. 
            # I will use random indices to ensure class balance.
            
            env_dataset = TransformedSubset(self.train_data_base, subset_indices, transform)
            loader = DataLoader(env_dataset, batch_size=self.batch_size, shuffle=True)
            loaders.append(loader)
            
        test_loader = DataLoader(self.test_data_base, batch_size=self.batch_size, shuffle=False)
        return loaders, test_loader

class TransformedSubset(torch.utils.data.Dataset):
    def __init__(self, dataset, indices, transform=None):
        self.dataset = dataset
        self.indices = indices
        self.transform = transform
        
    def __getitem__(self, idx):
        img, label = self.dataset[self.indices[idx]]
        # CIFAR10 returns PIL image
        if self.transform:
            img = self.transform(img)
        return img, label
        
    def __len__(self):
        return len(self.indices)
