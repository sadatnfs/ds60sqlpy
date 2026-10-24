"""llm-042: bounded local reference checks. No network or persistent data writes."""

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
    # Exercise 1: Freeze common questions
    import hashlib, json, time

    questions = [
        {"id": "q1", "family": "shape", "answerable": True},
        {"id": "q2", "family": "color", "answerable": True},
        {"id": "q3", "family": "astronomy", "answerable": False},
    ]
    fixture_hash = hashlib.sha256(json.dumps(questions, sort_keys=True).encode()).hexdigest()
    assert len({q["id"] for q in questions}) == 3 and questions[2]["answerable"] is False

    # Exercise 2: Compare saved candidate decisions
    results = {
        "tiny": {"q1": 1, "q2": 0, "q3": 0},
        "count": {"q1": 0, "q2": 0, "q3": 0},
        "retrieval": {"q1": 1, "q2": 1, "q3": 1},
    }
    ids = [q["id"] for q in questions]
    assert {name: sum(rows[i] for i in ids) for name, rows in results.items()} == {
        "tiny": 1,
        "count": 0,
        "retrieval": 3,
    }

    # Exercise 3: Run model mechanism checks
    torch.manual_seed(7)
    model = TinyDecoder()
    model.eval()
    tokens = torch.tensor([[2, 5, 7]])
    state = None
    parts = []
    start = time.perf_counter()
    with torch.no_grad():
        full, _ = model(tokens)
        for i in range(3):
            out, state = model(tokens[:, i : i + 1], state)
            parts.append(out)
    elapsed = time.perf_counter() - start
    torch.testing.assert_close(torch.cat(parts, 1), full, atol=1e-6, rtol=0)
    assert sum(p.numel() for p in model.parameters()) < 50000 and elapsed >= 0

    # Exercise 4: Bind lineage and budgets
    model_hash = hashlib.sha256(
        b"".join(p.detach().numpy().tobytes() for p in model.parameters())
    ).hexdigest()
    lineage = {
        "fixture": fixture_hash,
        "model": model_hash,
        "tokenizer": "literal-vocabulary-16",
        "context": 3,
        "generated_cap": 4,
        "elapsed_seconds": elapsed,
    }
    assert len(lineage["fixture"]) == len(lineage["model"]) == 64 and lineage["generated_cap"] == 4

    # Exercise 5: Apply an honest release gate
    gates = {
        "mechanism": True,
        "trust_boundary": True,
        "population_evidence": None,
        "severe_failures_absent": False,
    }
    decision = "go" if all(value is True for value in gates.values()) else "no-go"
    assert decision == "no-go"

    # Exercise 6: Write the reviewer decision
    report = {
        "decision": decision,
        "failure": "q3: tiny candidate answered without evidence",
        "missing": "independent held-out families",
        "next": "repair abstention and collect a new frozen evaluation",
        "limits": "authored local teaching fixture",
    }
    assert (
        report["decision"] == "no-go"
        and "q3" in report["failure"]
        and "families" in report["missing"]
    )
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
