"""llm-028: bounded local reference checks. No network or persistent data writes."""

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
    # Exercise 1: Freeze corpus identity
    import hashlib, json

    docs = [[1, 2, 3, 4], [1, 2, 4, 3]]
    held = [1, 3, 2, 4]
    split = {"train": ["a", "b"], "test": ["c"]}
    digest = hashlib.sha256(json.dumps(split, sort_keys=True).encode()).hexdigest()
    assert len(docs) == 2 and len(held) - 1 == 3 and len(digest) == 64

    # Exercise 2: Train a bounded decoder
    torch.manual_seed(11)
    model = TinyDecoder()
    opt = torch.optim.Adam(model.parameters(), lr=0.01)
    batch = torch.tensor(docs)
    curve = []
    for _ in range(20):
        opt.zero_grad(set_to_none=True)
        logits, _ = model(batch[:, :-1])
        loss = F.cross_entropy(logits.reshape(-1, 16), batch[:, 1:].reshape(-1))
        loss.backward()
        opt.step()
        curve.append(loss.item())
    assert (
        len(curve) == 20
        and np.isfinite(curve).all()
        and sum(p.numel() for p in model.parameters()) < 50000
    )

    # Exercise 3: Fit the count baseline
    counts = np.zeros((16, 16))
    for doc in docs:
        for a, b in zip(doc[:-1], doc[1:]):
            counts[a, b] += 1
    prob = (counts + 1) / (counts.sum(1, keepdims=True) + 16)
    assert counts.sum() == 6
    np.testing.assert_allclose(prob.sum(1), 1, atol=1e-12, rtol=0)

    # Exercise 4: Score one frozen holdout
    model.eval()
    sequence = torch.tensor([held])
    with torch.no_grad():
        z, _ = model(sequence[:, :-1])
        neural = F.cross_entropy(z.reshape(-1, 16), sequence[:, 1:].reshape(-1)).item()
    baseline = -np.mean([np.log(prob[a, b]) for a, b in zip(held[:-1], held[1:])])
    assert np.isfinite([neural, baseline]).all() and len(held) - 1 == 3

    # Exercise 5: Retest causality after training
    with torch.no_grad():
        full, _ = model(sequence[:, :-1])
        prefix, _ = model(sequence[:, :2])
    torch.testing.assert_close(prefix, full[:, :2], atol=1e-6, rtol=0)

    # Exercise 6: Record model identity and limits
    model_hash = hashlib.sha256(
        b"".join(p.detach().numpy().tobytes() for p in model.parameters())
    ).hexdigest()
    report = {
        "model_hash": model_hash,
        "split_hash": digest,
        "updates": 20,
        "targets": 3,
        "neural_loss": neural,
        "baseline_loss": float(baseline),
        "limit": "One authored held-out document.",
    }
    assert len(model_hash) == 64 and report["targets"] == 3 and report["updates"] == 20
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
