"""llm-applied-018: bounded local reference checks. No network or persistent data writes."""

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


class LoRAHead(nn.Module):
    def __init__(self, base, rank=2, alpha=2):
        super().__init__()
        self.base = base
        self.rank = rank
        self.scale = alpha / rank
        for parameter in base.parameters():
            parameter.requires_grad_(False)
        self.a = nn.Parameter(torch.randn(base.in_features, rank) * 0.02)
        self.b = nn.Parameter(torch.zeros(rank, base.out_features))

    def forward(self, x):
        return self.base(x) + (x @ self.a @ self.b) * self.scale


def objective(model, inputs, labels):
    logits, _ = model(inputs)
    return F.cross_entropy(logits.reshape(-1, model.vocab), labels.reshape(-1), ignore_index=-100)


def verify():
    # Exercise 1: Clone one base into two candidates
    torch.manual_seed(31)
    base = TinyDecoder()
    full = TinyDecoder()
    adapted = TinyDecoder()
    full.load_state_dict(base.state_dict())
    adapted.load_state_dict(base.state_dict())
    assert all(torch.equal(a, b) for a, b in zip(full.parameters(), adapted.parameters()))

    # Exercise 2: Install an output-head adapter
    for p in adapted.parameters():
        p.requires_grad_(False)
    adapted.output = LoRAHead(adapted.output, rank=2, alpha=2)
    sequence = torch.tensor([[1, 2, 5, 3], [1, 4, 6, 3]])
    inputs = sequence[:, :-1]
    labels = sequence[:, 1:].clone()
    labels[:, 0] = -100
    assert sum(p.numel() for p in adapted.parameters() if p.requires_grad) == 96
    with torch.no_grad():
        a, _ = base(inputs)
        b, _ = adapted(inputs)
        torch.testing.assert_close(a, b, atol=1e-6, rtol=0)

    # Exercise 3: Train both candidates under fixed budgets
    frozen = {
        name: p.detach().clone() for name, p in adapted.named_parameters() if not p.requires_grad
    }
    curves = {}
    for name, model, rate in [("full", full, 0.01), ("adapter", adapted, 0.03)]:
        opt = torch.optim.Adam([p for p in model.parameters() if p.requires_grad], lr=rate)
        curve = []
        for _ in range(20):
            opt.zero_grad(set_to_none=True)
            loss = objective(model, inputs, labels)
            curve.append(loss.item())
            loss.backward()
            opt.step()
        curves[name] = curve
        assert np.isfinite(curve).all() and curve[-1] < curve[0]

    # Exercise 4: Prove base preservation
    assert all(
        torch.equal(parameter.detach(), frozen[name])
        for name, parameter in adapted.named_parameters()
        if not parameter.requires_grad
    )

    # Exercise 5: Compare a frozen held-out task
    held = torch.tensor([[7, 2, 5, 3]])
    held_labels = held[:, 1:].clone()
    held_labels[:, 0] = -100
    results = {}
    for name, model in [("full", full), ("adapter", adapted)]:
        model.eval()
        with torch.no_grad():
            results[name] = objective(model, held[:, :-1], held_labels).item()
    assert set(results) == {"full", "adapter"} and np.isfinite(list(results.values())).all()

    # Exercise 6: Record comparison limits
    report = {
        "adapter_trainable": 96,
        "full_trainable": sum(p.numel() for p in full.parameters()),
        "steps": {"full": 20, "adapter": 20},
        "target_module": "output projection only",
        "scope": "literal-token teaching task",
        "heldout": results,
    }
    assert report["full_trainable"] > report["adapter_trainable"] and report["steps"] == {
        "full": 20,
        "adapter": 20,
    }
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
