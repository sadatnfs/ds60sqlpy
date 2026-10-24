"""llm-024: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


class TinyDecoder(nn.Module):
    def __init__(self, vocab=16, width=32, heads=2, context=32):
        super().__init__()
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
        if ids.ndim != 2 or ids.dtype != torch.long or ids.shape[1] == 0:
            raise ValueError("nonempty long batch,time IDs")
        offset = 0 if cache is None else cache["k"].shape[2]
        batch, time = ids.shape
        if offset + time > self.context or torch.any(ids < 0) or torch.any(ids >= self.vocab):
            raise ValueError("context or vocabulary limit")
        x = self.token(ids) + self.position(torch.arange(offset, offset + time))
        q, k, v = self.qkv(self.norm1(x)).chunk(3, dim=-1)

        def split(t):
            return t.reshape(batch, time, self.heads, self.width // self.heads).transpose(1, 2)

        q, k, v = map(split, (q, k, v))
        if cache is not None:
            if cache["k"].shape[0] != batch:
                raise ValueError("cache batch mismatch")
            k = torch.cat([cache["k"], k], dim=2)
            v = torch.cat([cache["v"], v], dim=2)
        allowed = torch.arange(k.shape[2])[None, :] <= torch.arange(offset, offset + time)[:, None]
        scores = q @ k.transpose(-2, -1) / (self.width // self.heads) ** 0.5
        weights = torch.softmax(scores.masked_fill(~allowed, float("-inf")), dim=-1)
        mixed = (weights @ v).transpose(1, 2).contiguous().reshape(batch, time, self.width)
        x = x + self.projection(mixed)
        x = x + self.feed(self.norm2(x))
        return self.output(x), {"k": k.detach(), "v": v.detach()}


def verify():
    # Exercise 1: Compute a full-prefix oracle
    torch.manual_seed(7)
    model = TinyDecoder()
    model.eval()
    ids = torch.tensor([[2, 5, 7, 3]])
    with torch.no_grad():
        full, _ = model(ids)
    assert tuple(full.shape) == (1, 4, 16)

    # Exercise 2: Run one token at a time
    cache = None
    outputs = []
    with torch.no_grad():
        for i in range(4):
            logits, cache = model(ids[:, i : i + 1], cache)
            outputs.append(logits)
    incremental = torch.cat(outputs, dim=1)
    torch.testing.assert_close(incremental, full, atol=1e-6, rtol=0)

    # Exercise 3: Inspect cache growth
    assert tuple(cache["k"].shape) == tuple(cache["v"].shape) == (1, 2, 4, 16)

    # Exercise 4: Bind ownership
    owned = {"request": "A", "model": "v1", "state": cache}

    def acquire(record, request, version):
        if record["request"] != request or record["model"] != version:
            raise ValueError("foreign cache")
        return record["state"]

    assert acquire(owned, "A", "v1") is cache
    try:
        acquire(owned, "B", "v1")
    except ValueError:
        pass
    else:
        raise AssertionError("cross-request cache accepted")

    # Exercise 5: Start a fresh request empty
    with torch.no_grad():
        fresh, _ = model(torch.tensor([[2]]), None)
    torch.testing.assert_close(fresh, full[:, :1], atol=1e-6, rtol=0)

    # Exercise 6: Invalidate after a model change
    try:
        acquire(owned, "A", "v2")
    except ValueError:
        pass
    else:
        raise AssertionError("stale cache accepted")
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
