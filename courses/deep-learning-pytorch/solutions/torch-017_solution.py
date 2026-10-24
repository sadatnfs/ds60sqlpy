"""torch-017: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Exercise 1: Calculate two penalties
    w = torch.tensor([1.0, -2.0])
    assert w.abs().sum().item() == 3 and w.square().sum().item() == 5

    # Exercise 2: Check evaluation dropout
    drop = nn.Dropout(0.5)
    drop.eval()
    x = torch.ones((4, 8))
    assert torch.equal(drop(x), x) and torch.equal(drop(x), x)

    # Exercise 3: Check training invariants
    drop.train()
    sampled = drop(x)
    assert tuple(sampled.shape) == (4, 8) and set(sampled.unique().tolist()) <= {0.0, 2.0}

    # Exercise 4: Separate data and penalty terms
    data_loss = torch.tensor(2.0)
    penalty = 0.1 * w.square().sum()
    assert penalty.item() == 0.5 and (data_loss + penalty).item() == 2.5

    # Exercise 5: Differentiate the explicit penalty
    v = torch.tensor([1.0, -2.0], requires_grad=True)
    (0.1 * v.square().sum()).backward()
    torch.testing.assert_close(v.grad, torch.tensor([0.2, -0.4]), atol=1e-6, rtol=0)

    # Exercise 6: Keep mode separate from gradients
    drop.eval()
    differentiable = torch.ones(3, requires_grad=True)
    observed = drop(differentiable)
    observed.sum().backward()
    assert observed.requires_grad and torch.equal(differentiable.grad, torch.ones(3))
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
