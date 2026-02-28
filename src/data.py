import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import numpy as np


def get_transforms():
    """Returns the list of transforms for each of the 5 drift environments."""
    # Env 0: Clean
    t0 = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])

    # Env 1: Fog (simulated via gamma correction to wash out image)
    t1 = transforms.Compose([
        transforms.ToTensor(),
        transforms.Lambda(lambda x: transforms.functional.adjust_gamma(x, gamma=0.5)),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])

    # Env 2: Night (low brightness and contrast)
    t2 = transforms.Compose([
        transforms.ColorJitter(brightness=0.2, contrast=0.5, saturation=0.5),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])

    # Env 3: Snow (low saturation, high brightness whitewash)
    t3 = transforms.Compose([
        transforms.ColorJitter(saturation=0.1, brightness=1.2),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])

    # Env 4: Blur (Gaussian blur with kernel=5, sigma=2.0)
    t4 = transforms.Compose([
        transforms.ToTensor(),
        transforms.GaussianBlur(kernel_size=5, sigma=2.0),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])

    return [t0, t1, t2, t3, t4]


class DriftCIFAR10:
    """
    CIFAR-10 split into 5 sequential environments with distribution drift.
    Each environment uses 5000 randomly sampled training images with a distinct transform.
    Test evaluation is always on the clean CIFAR-10 test set.
    """

    def __init__(self, root='./data', download=True, batch_size=64):
        self.root = root
        self.batch_size = batch_size
        self.transforms_list = get_transforms()

        self.train_data_base = datasets.CIFAR10(root=root, train=True, download=download)
        self.test_data_base = datasets.CIFAR10(
            root=root, train=False, download=download,
            transform=self.transforms_list[0]  # evaluate on clean test set
        )

    def get_loaders(self):
        """Returns (task_loaders, test_loader) where task_loaders is a list of per-environment DataLoaders."""
        loaders = []

        # Random permutation ensures class balance across all 5 environments
        indices = np.random.permutation(len(self.train_data_base))

        for i, transform in enumerate(self.transforms_list):
            start = i * 5000
            end = (i + 1) * 5000
            subset_indices = indices[start:end]

            env_dataset = TransformedSubset(self.train_data_base, subset_indices, transform)
            loader = DataLoader(env_dataset, batch_size=self.batch_size, shuffle=True)
            loaders.append(loader)

        test_loader = DataLoader(self.test_data_base, batch_size=self.batch_size, shuffle=False)
        return loaders, test_loader


class TransformedSubset(torch.utils.data.Dataset):
    """Dataset wrapper that applies a specific transform to a subset of indices."""

    def __init__(self, dataset, indices, transform=None):
        self.dataset = dataset
        self.indices = indices
        self.transform = transform

    def __getitem__(self, idx):
        img, label = self.dataset[self.indices[idx]]
        if self.transform:
            img = self.transform(img)
        return img, label

    def __len__(self):
        return len(self.indices)
