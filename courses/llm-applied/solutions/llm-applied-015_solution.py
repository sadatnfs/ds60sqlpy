"""llm-applied-015: bounded local reference checks. No network or persistent data writes."""

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


def objective(model, inputs, labels):
    logits, _ = model(inputs)
    return F.cross_entropy(logits.reshape(-1, model.vocab), labels.reshape(-1), ignore_index=-100)


def verify():
    # Exercise 1: Build an explicit SFT batch
    torch.manual_seed(23)
    model = TinyDecoder()
    sequences = torch.tensor([[1, 2, 5, 3], [1, 4, 6, 3]])
    inputs = sequences[:, :-1]
    labels = sequences[:, 1:].clone()
    labels[:, 0] = -100
    assert (
        tuple(inputs.shape) == (2, 3)
        and labels.tolist() == [[-100, 5, 3], [-100, 6, 3]]
        and int((labels != -100).sum()) == 4
    )

    # Exercise 2: Measure the initial state
    held = torch.tensor([[7, 2, 5, 3]])
    held_labels = held[:, 1:].clone()
    held_labels[:, 0] = -100
    with torch.no_grad():
        initial_train = objective(model, inputs, labels).item()
        initial_held = objective(model, held[:, :-1], held_labels).item()
    count = sum(p.numel() for p in model.parameters() if p.requires_grad)
    assert (
        np.isfinite([initial_train, initial_held]).all()
        and 0 < count < 50000
        and all(p.requires_grad for p in model.parameters())
    )

    # Exercise 3: Perform actual full fine-tuning
    before = model.token.weight.detach().clone()
    opt = torch.optim.Adam(model.parameters(), lr=0.01)
    curve = []
    for _ in range(20):
        opt.zero_grad(set_to_none=True)
        loss = objective(model, inputs, labels)
        curve.append(loss.item())
        loss.backward()
        opt.step()
    assert len(curve) == 20 and np.isfinite(curve).all() and curve[-1] < curve[0]
    assert not torch.equal(before, model.token.weight.detach())

    # Exercise 4: Inspect the mask derivative
    probe = torch.zeros((2, 3, 16), requires_grad=True)
    F.cross_entropy(probe.reshape(-1, 16), labels.reshape(-1), ignore_index=-100).backward()
    assert (
        torch.count_nonzero(probe.grad[:, 0]).item() == 0
        and torch.count_nonzero(probe.grad[:, 1:]).item() > 0
    )

    # Exercise 5: Evaluate the frozen held-out prompt
    model.eval()
    saved = model.output.weight.detach().clone()
    with torch.no_grad():
        final_held = objective(model, held[:, :-1], held_labels).item()
        final_train = objective(model, inputs, labels).item()
    assert np.isfinite(final_held) and torch.equal(saved, model.output.weight.detach())

    # Exercise 6: Write an honest adaptation receipt
    receipt = {
        "updates": 20,
        "active_training_targets": 4,
        "initial_train": initial_train,
        "final_train": final_train,
        "initial_held": initial_held,
        "final_held": final_held,
        "scope": "literal token task, not a pretrained subject assistant",
    }
    assert (
        receipt["updates"] == 20
        and receipt["active_training_targets"] == 4
        and "not a pretrained" in receipt["scope"]
    )
    with torch.no_grad():
        np.testing.assert_allclose(
            receipt["final_train"], objective(model, inputs, labels).item(), atol=1e-12, rtol=0
        )
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
