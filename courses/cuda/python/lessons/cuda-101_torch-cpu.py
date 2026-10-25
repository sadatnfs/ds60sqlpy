"""Bounded PyTorch lesson with explicit execution device."""

import torch

torch.set_num_threads(1)
device = torch.device("cpu")

base = torch.eye(4, device=device)
base.requires_grad_(False)
a = torch.nn.Parameter(torch.ones((4, 1), device=device) * 0.1)
b = torch.nn.Parameter(torch.zeros((1, 4), device=device))
x = torch.ones((2, 4), device=device)
optimizer = torch.optim.SGD([a, b], lr=0.1)
loss = (x @ (base + a @ b)).square().mean()
loss.backward()
optimizer.step()
assert base.grad is None
assert a.numel() + b.numel() == 8 and base.numel() == 16
assert torch.isfinite(a).all() and torch.isfinite(b).all()
print("PyTorch adapter census: base16 frozen; trainable8; base storage remains")
