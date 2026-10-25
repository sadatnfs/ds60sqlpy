"""Bounded PyTorch lesson with explicit execution device."""

import torch

torch.set_num_threads(1)
if not torch.cuda.is_available() or torch.version.hip is not None:
    raise RuntimeError("This variant requires NVIDIA CUDA, not CPU or ROCm fallback")
device = torch.device("cuda:0")

x = torch.ones((8, 16), device=device, requires_grad=True)
loss = x.square().mean()
loss.backward()
logical_bytes = x.numel() * x.element_size()
assert logical_bytes == 512
assert x.grad is not None and torch.isfinite(x.grad).all()
print("PyTorch input payload:", logical_bytes, "bytes; excludes gradients, context and reserve")
if device.type == "cuda":
    torch.cuda.synchronize()
    print("Allocated:", torch.cuda.memory_allocated(), "reserved:", torch.cuda.memory_reserved())
torch.cuda.synchronize()
