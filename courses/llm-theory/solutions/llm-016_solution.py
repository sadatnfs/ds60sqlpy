"""llm-016: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

class TinyDecoder(nn.Module):
    def __init__(self, vocab=16, width=32, heads=2, context=32):
        super().__init__()
        dimensions = (vocab, width, heads, context)
        if any(type(value) is not int or value <= 0 for value in dimensions):
            raise ValueError("positive integer dimensions are required")
        if width % heads != 0:
            raise ValueError("model width must be divisible by head count")
        self.vocab, self.width, self.heads, self.context = vocab, width, heads, context
        self.token = nn.Embedding(vocab, width)
        self.position = nn.Embedding(context, width)
        self.norm1 = nn.LayerNorm(width)
        self.qkv = nn.Linear(width, 3 * width, bias=False)
        self.projection = nn.Linear(width, width, bias=False)
        self.norm2 = nn.LayerNorm(width)
        self.feed = nn.Sequential(
            nn.Linear(width, 2 * width), nn.ReLU(), nn.Linear(2 * width, width)
        )
        self.output = nn.Linear(width, vocab, bias=False)

    def forward(self, ids, cache=None):
        if (
            ids.ndim != 2
            or ids.dtype != torch.long
            or ids.shape[0] == 0
            or ids.shape[1] == 0
        ):
            raise ValueError("nonempty long batch,time IDs")
        offset = 0 if cache is None else cache["k"].shape[2]
        batch, time = ids.shape
        if (
            offset + time > self.context
            or torch.any(ids < 0)
            or torch.any(ids >= self.vocab)
        ):
            raise ValueError("context or vocabulary limit")
        x = self.token(ids) + self.position(torch.arange(offset, offset + time))
        q, k, v = self.qkv(self.norm1(x)).chunk(3, dim=-1)

        def split(t):
            return t.reshape(
                batch, time, self.heads, self.width // self.heads
            ).transpose(1, 2)

        q, k, v = map(split, (q, k, v))
        if cache is not None:
            if cache["k"].shape[0] != batch:
                raise ValueError("cache batch mismatch")
            k = torch.cat([cache["k"], k], dim=2)
            v = torch.cat([cache["v"], v], dim=2)
        allowed = (
            torch.arange(k.shape[2])[None, :]
            <= torch.arange(offset, offset + time)[:, None]
        )
        scores = q @ k.transpose(-2, -1) / (self.width // self.heads) ** 0.5
        weights = torch.softmax(scores.masked_fill(~allowed, float("-inf")), dim=-1)
        mixed = (
            (weights @ v).transpose(1, 2).contiguous().reshape(batch, time, self.width)
        )
        x = x + self.projection(mixed)
        x = x + self.feed(self.norm2(x))
        return self.output(x), {"k": k.detach(), "v": v.detach()}



def verify():
    # Exercise 1: Build a bounded decoder
    torch.manual_seed(7)
    model = TinyDecoder().eval()
    count = sum(parameter.numel() for parameter in model.parameters())
    assert count == 10464
    assert count < 50000

    # Exercise 2: Trace output axes
    torch.manual_seed(7)
    model = TinyDecoder().eval()
    ids = torch.tensor([[2, 5, 7, 3]], dtype=torch.long)
    with torch.no_grad():
        logits, _ = model(ids)
    assert tuple(logits.shape) == (1, 4, 16)
    assert logits.dtype == torch.float32
    assert torch.isfinite(logits).all()

    # Exercise 3: Recompute prefixes
    torch.manual_seed(7)
    model = TinyDecoder().eval()
    ids = torch.tensor([[2, 5, 7, 3]], dtype=torch.long)
    with torch.no_grad():
        full, _ = model(ids)
        for length in range(1, 5):
            prefix, _ = model(ids[:, :length])
            torch.testing.assert_close(prefix, full[:, :length], atol=1e-6, rtol=0)

    # Exercise 4: Perturb only future tokens
    torch.manual_seed(7)
    model = TinyDecoder().eval()
    ids = torch.tensor([[2, 5, 7, 3]], dtype=torch.long)
    changed = ids.clone()
    changed[:, 2:] = torch.tensor([[8, 9]])
    with torch.no_grad():
        original, _ = model(ids)
        perturbed, _ = model(changed)
    torch.testing.assert_close(perturbed[:, :2], original[:, :2], atol=1e-6, rtol=0)
    assert not torch.equal(ids, changed)

    # Exercise 5: Inspect head shapes
    torch.manual_seed(7)
    model = TinyDecoder().eval()
    ids = torch.tensor([[2, 5, 7, 3]], dtype=torch.long)
    logits, cache = model(ids)
    assert logits.requires_grad
    for tensor in cache.values():
        assert tuple(tensor.shape) == (1, 2, 4, 16)
        assert tensor.dtype == torch.float32
        assert not tensor.requires_grad
    assert sum(tensor.numel() * tensor.element_size() for tensor in cache.values()) == 1024

    # Exercise 6: Reject invalid token IDs
    model = TinyDecoder().eval()
    invalid_inputs = [
        torch.tensor([[16]], dtype=torch.long),
        torch.tensor([[-1]], dtype=torch.long),
        torch.zeros((1, 33), dtype=torch.long),
        torch.zeros((1, 0), dtype=torch.long),
        torch.tensor([[2.0]], dtype=torch.float32),
    ]
    for invalid in invalid_inputs:
        try:
            model(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid token/context contract was accepted')
    for options in [dict(width=5, heads=2), dict(heads=0), dict(context=0)]:
        try:
            TinyDecoder(**options)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid model dimensions were accepted')
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
