import torch
import torch.nn as nn
import timm
from copy import deepcopy


def get_model(num_classes=10, pretrained=True):
    """
    MobileNetV3-Small (0.5x width) with reduced head for edge deployment.
    Base model: ~580K params. Conv head reduced 1024->128 channels to ~310K params.
    """
    model = timm.create_model('mobilenetv3_small_050', pretrained=pretrained, num_classes=num_classes)

    # Reduce conv_head from 1024 -> 128 channels to minimise parameter count
    if hasattr(model, 'conv_head'):
        prev_channels = model.conv_head.in_channels
        new_channels = 128
        model.conv_head = nn.Conv2d(prev_channels, new_channels, kernel_size=1, bias=True)
        model.classifier = nn.Linear(new_channels, num_classes)

    return model


class EWC(nn.Module):
    """Elastic Weight Consolidation regulariser (diagonal Fisher approximation)."""

    def __init__(self, model: nn.Module, loader, device, lambda_ewc=1e4):
        super().__init__()
        self.model = model
        self.lambda_ewc = lambda_ewc
        self.device = device

        # Store parameter snapshot and initialise Fisher diagonal
        self.params_copy = {}
        self.fisher = {}

        for name, param in model.named_parameters():
            if param.requires_grad:
                self.params_copy[name] = param.clone().detach()
                self.fisher[name] = torch.zeros_like(param)

        self._compute_fisher(loader)

    def _compute_fisher(self, loader):
        """Compute diagonal empirical Fisher Information Matrix."""
        self.model.eval()
        criterion = nn.CrossEntropyLoss()

        print("Computing Fisher Matrix...")
        for x, y in loader:
            x, y = x.to(self.device), y.to(self.device)
            self.model.zero_grad()
            output = self.model(x)
            loss = criterion(output, y)
            loss.backward()

            for name, param in self.model.named_parameters():
                if param.requires_grad and param.grad is not None:
                    self.fisher[name] += param.grad.data ** 2 / len(loader)

        print("Fisher Matrix computed.")

    def penalty(self, current_model):
        """EWC penalty: λ * Σ F_i * (θ_i - θ*_i)^2"""
        loss = 0
        for name, param in current_model.named_parameters():
            if name in self.fisher:
                fisher = self.fisher[name]
                old_param = self.params_copy[name]
                loss += (fisher * (param - old_param) ** 2).sum()
        return self.lambda_ewc * loss


if __name__ == "__main__":
    import torchinfo
    m = get_model()
    torchinfo.summary(m, (1, 3, 32, 32))
