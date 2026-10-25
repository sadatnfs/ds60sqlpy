"""Bounded PyTorch lesson with explicit execution device."""

import torch

torch.set_num_threads(1)
device = torch.device("cpu")

x = torch.tensor([1.0, 2.0, 3.0, 4.0], device=device).reshape(1, 1, 4)
kernel = torch.tensor([1.0, -1.0], device=device).reshape(1, 1, 2)
y = torch.nn.functional.conv1d(x, kernel)
assert torch.allclose(y, torch.full((1, 1, 3), -1.0, device=device))
print("PyTorch cross-correlation:", y.cpu().tolist())
