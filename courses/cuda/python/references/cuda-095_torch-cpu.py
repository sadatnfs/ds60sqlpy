"""Bounded PyTorch lesson with explicit execution device."""

import torch

torch.set_num_threads(1)
device = torch.device("cpu")

model = torch.nn.Sequential(torch.nn.Linear(2, 1, bias=False), torch.nn.Dropout(0.5)).to(device)
with torch.no_grad():
    model[0].weight.copy_(torch.tensor([[2.0, -1.0]], device=device))
model.eval()
with torch.inference_mode():
    y = model(torch.tensor([[1.0, 3.0], [2.0, 1.0]], device=device))
assert torch.allclose(y, torch.tensor([[-1.0], [3.0]], device=device))
print("PyTorch evaluation output:", y.cpu().tolist())
