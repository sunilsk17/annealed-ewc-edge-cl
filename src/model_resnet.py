"""
ResNet-18 Model for CIFAR Continual Learning

Standard ResNet-18 architecture adapted for CIFAR (32x32 images).
Compatible with existing EWC implementation.
"""

import torch
import torch.nn as nn
import torchvision.models as models

def get_resnet18_cifar(num_classes=10):
    """
    Get standard ResNet-18 adapted for CIFAR datasets.
    
    Modifications from ImageNet ResNet-18:
    - First conv: 7x7 stride 2 → 3x3 stride 1 (for 32x32 input)
    - No maxpool after first conv (preserve spatial resolution)
    - Rest of architecture unchanged (standard)
    
    This configuration is standard in continual learning literature.
    
    Args:
        num_classes: Number of output classes (10 for CIFAR-10, 100 for CIFAR-100)
        
    Returns:
        ResNet-18 model configured for CIFAR
    """
    # Start with standard ResNet-18
    model = models.resnet18(weights=None)
    
    # Adapt for CIFAR (32x32 images)
    # Standard modification used in CL papers
    model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
    model.maxpool = nn.Identity()  # Remove maxpool for small images
    
    # Adapt final layer for num_classes
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    
    return model

def count_parameters(model):
    """Count trainable parameters."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

class ResNet18EWC:
    """
    ResNet-18 with EWC support.
    
    Wrapper to maintain compatibility with existing EWC implementation.
    """
    def __init__(self, num_classes=10):
        self.num_classes = num_classes
        self.model = get_resnet18_cifar(num_classes)
        
    def to(self, device):
        self.model = self.model.to(device)
        return self
    
    def __call__(self, x):
        return self.model(x)
    
    def parameters(self):
        return self.model.parameters()
    
    def named_parameters(self):
        return self.model.named_parameters()
    
    def train(self):
        self.model.train()
    
    def eval(self):
        self.model.eval()
    
    def state_dict(self):
        return self.model.state_dict()
    
    def load_state_dict(self, state_dict):
        self.model.load_state_dict(state_dict)

if __name__ == '__main__':
    # Test model creation
    print("="*60)
    print("Testing ResNet-18 CIFAR Configuration")
    print("="*60)
    
    # CIFAR-10
    model_c10 = get_resnet18_cifar(num_classes=10)
    params_c10 = count_parameters(model_c10)
    print(f"\nCIFAR-10 Model:")
    print(f"  Parameters: {params_c10:,} (~{params_c10/1e6:.2f}M)")
    
    # Test forward pass
    x = torch.randn(4, 3, 32, 32)
    y = model_c10(x)
    print(f"  Input shape: {x.shape}")
    print(f"  Output shape: {y.shape}")
    print(f"  ✓ CIFAR-10 model working")
    
    # CIFAR-100
    model_c100 = get_resnet18_cifar(num_classes=100)
    params_c100 = count_parameters(model_c100)
    print(f"\nCIFAR-100 Model:")
    print(f"  Parameters: {params_c100:,} (~{params_c100/1e6:.2f}M)")
    
    y = model_c100(x)
    print(f"  Input shape: {x.shape}")
    print(f"  Output shape: {y.shape}")
    print(f"  ✓ CIFAR-100 model working")
    
    # MPS compatibility check
    if torch.backends.mps.is_available():
        print(f"\n✓ MPS (Apple Silicon) available")
        model_c10 = model_c10.to('mps')
        x_mps = x.to('mps')
        y_mps = model_c10(x_mps)
        print(f"  ✓ MPS forward pass successful")
    
    print(f"\n{'='*60}")
    print("✓ ResNet-18 implementation verified!")
    print("  Standard architecture for continual learning")
    print(f"  Parameters: ~11.2M (36× larger than MobileNetV3)")
    print(f"{'='*60}")
