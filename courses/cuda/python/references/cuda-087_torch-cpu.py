"""Bounded PyTorch lesson with explicit execution device."""

import torch

torch.set_num_threads(1)
device = torch.device("cpu")

x = torch.tensor([1.0, 2.0], device=device)
y = torch.tensor([2.0, 4.0], device=device)
w = torch.tensor(0.0, device=device, requires_grad=True)
optimizer = torch.optim.SGD([w], lr=0.1)
loss = ((w * x - y) ** 2).mean()
loss.backward()
assert torch.allclose(w.grad, torch.tensor(-10.0, device=device))
optimizer.step()
assert torch.allclose(w, torch.tensor(1.0, device=device))
print("PyTorch one-step weight:", float(w.detach().cpu()), "device", w.device)
