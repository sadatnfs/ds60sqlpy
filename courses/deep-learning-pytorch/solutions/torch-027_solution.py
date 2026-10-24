"""torch-027: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Exercise 1: Freeze a known base
    base = nn.Linear(2, 2, bias=False)
    with torch.no_grad():
        base.weight.copy_(torch.eye(2))
    for parameter in base.parameters():
        parameter.requires_grad_(False)
        parameter.grad = None
    x = torch.tensor([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    assert torch.equal(base(x), x) and not any(p.requires_grad for p in base.parameters())

    # Exercise 2: Train a new head
    head = nn.Linear(2, 1, bias=False)
    with torch.no_grad():
        head.weight.zero_()
    base_before = base.weight.detach().clone()
    head_before = head.weight.detach().clone()
    target = torch.tensor([[1.0], [2.0], [3.0]])
    optimizer = torch.optim.SGD(head.parameters(), lr=0.1)
    optimizer.zero_grad(set_to_none=True)
    loss = (head(base(x)) - target).square().mean()
    loss.backward()
    optimizer.step()
    assert not torch.equal(head.weight, head_before) and torch.equal(base.weight, base_before)

    # Exercise 3: Inspect absent base gradients
    assert base.weight.grad is None and head.weight.grad is not None

    # Exercise 4: Expose buffer updates despite freezing
    normalizer = nn.BatchNorm1d(2, momentum=0.5)
    for parameter in normalizer.parameters():
        parameter.requires_grad_(False)
    before = normalizer.running_mean.clone()
    normalizer.train()
    normalizer(torch.tensor([[1.0, 3.0], [3.0, 5.0]]))
    assert not torch.equal(before, normalizer.running_mean)

    # Exercise 5: Freeze normalization behavior with eval
    normalizer.eval()
    fixed = normalizer.running_mean.clone()
    normalizer(torch.tensor([[100.0, 200.0]]))
    assert torch.equal(fixed, normalizer.running_mean)

    # Exercise 6: Begin an explicit unfreeze phase
    for parameter in base.parameters():
        parameter.requires_grad_(True)
    combined = torch.optim.SGD(list(base.parameters()) + list(head.parameters()), lr=0.01)
    combined.zero_grad(set_to_none=True)
    (head(base(x)) - target).square().mean().backward()
    combined.step()
    assert not torch.equal(base.weight, base_before)
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
