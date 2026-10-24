"""llm-018: bounded local reference checks. No network or persistent data writes."""

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
    # Exercise 1: Prepare a tiny training batch
    torch.manual_seed(7)
    model = TinyDecoder()
    ids = torch.tensor([[1, 2, 3, 4], [2, 3, 4, 5]])
    inputs = ids[:, :-1]
    targets = ids[:, 1:]
    assert tuple(inputs.shape) == (2, 3) and targets.numel() == 6

    # Exercise 2: Measure the initial objective
    logits, _ = model(inputs)
    initial = F.cross_entropy(logits.reshape(-1, 16), targets.reshape(-1)).item()
    assert np.isfinite(initial) and initial > 0

    # Exercise 3: Perform twelve bounded updates
    opt = torch.optim.Adam(model.parameters(), lr=0.01)
    before = model.output.weight.detach().clone()
    losses = []
    norms = []
    for _ in range(12):
        opt.zero_grad(set_to_none=True)
        logits, _ = model(inputs)
        loss = F.cross_entropy(logits.reshape(-1, 16), targets.reshape(-1))
        loss.backward()
        norm = (
            sum(float(p.grad.square().sum()) for p in model.parameters() if p.grad is not None)
            ** 0.5
        )
        losses.append(loss.item())
        norms.append(norm)
        opt.step()
    assert len(losses) == 12 and np.isfinite(losses + norms).all() and max(norms) > 0

    # Exercise 4: Verify actual parameter change
    assert not torch.equal(before, model.output.weight.detach())

    # Exercise 5: Clear accumulated gradients
    opt.zero_grad(set_to_none=True)
    assert all(p.grad is None for p in model.parameters())

    # Exercise 6: Report budget honestly
    report = {
        "steps": 12,
        "maximum_steps": 200,
        "initial_loss": initial,
        "last_training_loss": losses[-1],
        "convergence_established": False,
    }
    assert report["steps"] <= report["maximum_steps"] and report["convergence_established"] is False
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
