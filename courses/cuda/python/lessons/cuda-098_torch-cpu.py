"""Bounded PyTorch lesson with explicit execution device."""

import torch

torch.set_num_threads(1)
device = torch.device("cpu")

x = torch.tensor([2.0, -2.0], dtype=torch.float64, device=device, requires_grad=True)
y = torch.relu(2 * x + 1).sum()
y.backward()
assert torch.allclose(x.grad, torch.tensor([2.0, 0.0], dtype=torch.float64, device=device))
assert torch.autograd.gradcheck(lambda z: torch.relu(2 * z + 1), (x.detach().requires_grad_(),))
print("PyTorch gradient reference:", x.grad.cpu().tolist())
