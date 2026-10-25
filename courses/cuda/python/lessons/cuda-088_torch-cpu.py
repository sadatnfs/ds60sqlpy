"""Bounded PyTorch lesson with explicit execution device."""

import torch
from torch.utils.data import DataLoader, TensorDataset

torch.set_num_threads(1)
device = torch.device("cpu")

x = torch.arange(8, dtype=torch.float32).reshape(4, 2)
loader = DataLoader(
    TensorDataset(x), batch_size=2, shuffle=False, num_workers=0, pin_memory=(device.type == "cuda")
)
observed = []
for (batch,) in loader:
    values = batch.to(device, non_blocking=(device.type == "cuda"))
    observed.extend(values.sum(dim=1).cpu().tolist())
assert observed == [1.0, 5.0, 9.0, 13.0]
print("PyTorch bounded input pipeline:", observed)
