"""torch-017: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Worked example A: Calculate two penalties
    w = torch.tensor([1.0, -2.0])
    assert w.abs().sum().item() == 3 and w.square().sum().item() == 5

    # Worked example B: Check evaluation dropout
    drop = nn.Dropout(0.5)
    drop.eval()
    x = torch.ones((4, 8))
    assert torch.equal(drop(x), x) and torch.equal(drop(x), x)

    # Worked example C: Check training invariants
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

    # Exercise 1: Compute penalties for a new vector
    penalized = torch.tensor([3.0, -4.0, 0.0])
    assert penalized.abs().sum().item() == 7 and penalized.square().sum().item() == 25

    # Exercise 2: Predict train-mode values for p=0.25
    quarter = nn.Dropout(0.25)
    quarter.train()
    kept = quarter(torch.ones((3, 5)))
    assert tuple(kept.shape) == (3, 5) and all(
        value == 0 or abs(value - 4 / 3) < 1e-6 for value in kept.flatten().tolist()
    )

    # Exercise 3: Confirm eval disables the new rate
    quarter.eval()
    assert torch.equal(quarter(torch.ones((3, 5))), torch.ones((3, 5)))
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
