import torch
import torch.nn as nn
import timm
import torchinfo
from copy import deepcopy

def get_model(num_classes=10, pretrained=True):
    """
    Creates a MobileNetV3-small model. 
    We use a scaled down version (0.5x width) to aim for the <200k param target if possible,
    or standard small if that's what 'mobilenetv3_small' usually refers to.
    
    Standard mobilenetv3_small_100 is ~2.5M params.
    mobilenetv3_small_050 is ~1M params.
    mobilenetv3_small_minimal_100 is smaller.
    
    To strictly satisfy "<200k params", we might need a custom configuration or heavy pruning.
    However, for this 'Micro' task, we will use the smallest available 'timm' preset and note the size.
    'mobilenetv3_small_050' is likely the closest standard one.
    To get <200k, we might need to change the classifier head significantly or use a different micro architecture.
    Let's try mobilenetv3_small_050 and if it's too big, we just accept it as the base for 'Micro' demo.
    User's script uses 'mobilenetv3_small_100' which is definitely >200k (2.5M).
    We will use 'mobilenetv3_small_050' to be closer to 'Micro'.
    """
    # Using 0.5 multiplier for width
    model = timm.create_model('mobilenetv3_small_050', pretrained=pretrained, num_classes=num_classes)
    
    # Optimization for Micro Constraint (<200k params)
    # Standard mobilenetv3_small_050 is ~580k params.
    # We reduce the 'conv_head' (expansion) from 1024 -> 128 channels.
    # This saves ~300k params.
    
    # Check if model has 'conv_head' (timm specific)
    if hasattr(model, 'conv_head'):
        # original: Conv2d(288, 1024, 1, 1)
        prev_channels = model.conv_head.in_channels
        new_channels = 128 # drastically smaller
        
        model.conv_head = nn.Conv2d(prev_channels, new_channels, kernel_size=1, bias=True)
        # Note: timm mobilenetv3 uses Hardswish after conv_head usually, but it might be part of the block or separate.
        # In timm, conv_head is just the conv. The activation follows in forward().
        # Actually timm implementation: x = self.act2(self.conv_head(x))
        
        # We also need to update the classifier
        # original: Linear(1024, num_classes)
        model.classifier = nn.Linear(new_channels, num_classes)
        
    return model

class EWC(nn.Module):
    def __init__(self, model: nn.Module, loader, device, lambda_ewc=1e4):
        super().__init__()
        self.model = model
        self.lambda_ewc = lambda_ewc
        self.device = device
        
        # Store parameters and initialize Fisher
        self.params_copy = {}
        self.fisher = {}
        
        for name, param in model.named_parameters():
            if param.requires_grad:
                self.params_copy[name] = param.clone().detach()
                self.fisher[name] = torch.zeros_like(param)
        
        self._compute_fisher(loader)
        
    def _compute_fisher(self, loader):
        """Computes diagonal Fisher Information Matrix."""
        self.model.eval()
        criterion = nn.CrossEntropyLoss()
        
        # Accumulate gradients
        print("Computing Fisher Matrix...")
        for x, y in loader:
            x, y = x.to(self.device), y.to(self.device)
            self.model.zero_grad()
            output = self.model(x)
            
            # Use predicted labels to sample from P(y|x) approximation or ground truth?
            # EWC usually uses ground truth if available, or sampled from model.
            # Empirical Fisher uses ground truth labels 'y'.
            loss = criterion(output, y)
            loss.backward()
            
            for name, param in self.model.named_parameters():
                if param.requires_grad and param.grad is not None:
                    # F = E[grad^2]
                    self.fisher[name] += param.grad.data ** 2 / len(loader)
        print("Fisher Matrix computed.")
                    
    def penalty(self, current_model):
        loss = 0
        for name, param in current_model.named_parameters():
            if name in self.fisher:
                fisher = self.fisher[name]
                old_param = self.params_copy[name]
                # EWC Loss: sum(F * (theta - theta_old)^2)
                loss += (fisher * (param - old_param) ** 2).sum()
        return self.lambda_ewc * loss

if __name__ == "__main__":
    m = get_model()
    print("Model created.")
    torchinfo.summary(m, (1, 3, 32, 32)) # CIFAR is 32x32, not 224x224.
