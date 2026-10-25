"""Bounded PyTorch lesson with explicit execution device."""

import copy

import torch

torch.set_num_threads(1)
device = torch.device("cpu")

w = torch.nn.Parameter(torch.tensor(1.0, device=device))
optimizer = torch.optim.SGD([w], lr=0.1, momentum=0.9)
for _ in range(2):
    optimizer.zero_grad()
    w.square().backward()
    optimizer.step()
saved_weight = w.detach().clone()
saved_optimizer = copy.deepcopy(optimizer.state_dict())
optimizer.zero_grad()
w.square().backward()
optimizer.step()
expected = w.detach().clone()
with torch.no_grad():
    w.copy_(saved_weight)
optimizer.load_state_dict(saved_optimizer)
optimizer.zero_grad()
w.square().backward()
optimizer.step()
assert torch.allclose(w, expected)
print("PyTorch in-memory checkpoint continuation:", float(w.detach().cpu()))
