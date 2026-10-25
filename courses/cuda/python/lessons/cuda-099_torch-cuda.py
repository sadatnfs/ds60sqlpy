"""Bounded PyTorch lesson with explicit execution device."""

import torch

torch.set_num_threads(1)
if not torch.cuda.is_available() or torch.version.hip is not None:
    raise RuntimeError("This variant requires NVIDIA CUDA, not CPU or ROCm fallback")
device = torch.device("cuda:0")

x = torch.tensor([1.0, 2.0, 3.0, 4.0], device=device)
y = 2 * x
full = torch.tensor(0.0, device=device, requires_grad=True)
((full * x - y) ** 2).mean().backward()
small = torch.tensor(0.0, device=device, requires_grad=True)
for a, b in [(x[:3], y[:3]), (x[3:], y[3:])]:
    (((small * a - b) ** 2).sum() / x.numel()).backward()
assert torch.allclose(full.grad, small.grad)
print("PyTorch unequal microbatch gradient:", float(small.grad.cpu()))
torch.cuda.synchronize()
