"""Bounded PyTorch lesson with explicit execution device."""

import torch

torch.set_num_threads(1)
if not torch.cuda.is_available() or torch.version.hip is not None:
    raise RuntimeError("This variant requires NVIDIA CUDA, not CPU or ROCm fallback")
device = torch.device("cuda:0")

q = torch.tensor([[[[1.0, 0.0], [0.0, 1.0]]]], device=device)
k = q.clone()
v = torch.tensor([[[[2.0, 3.0], [4.0, 5.0]]]], device=device)
scores = q @ k.transpose(-2, -1) / (2**0.5)
mask = torch.ones((2, 2), dtype=torch.bool, device=device).tril()
reference = torch.softmax(scores.masked_fill(~mask, float("-inf")), dim=-1) @ v
actual = torch.nn.functional.scaled_dot_product_attention(q, k, v, is_causal=True)
assert torch.allclose(actual, reference, atol=1e-5, rtol=1e-5)
print("PyTorch attention parity:", actual.cpu().tolist(), "; selected kernel backend not inferred")
torch.cuda.synchronize()
