"""llm-015: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Exercise 1: Derive a scalar gradient
    w = torch.tensor(0.0, dtype=torch.float64, requires_grad=True)
    loss = (w - 2) ** 2
    loss.backward()
    assert w.grad.item() == -4 and loss.item() == 4

    # Exercise 2: Compare finite differences
    h = 0.001
    numeric = (((h - 2) ** 2) - ((-h - 2) ** 2)) / (2 * h)
    np.testing.assert_allclose(numeric, -4, atol=1e-10, rtol=0)

    # Exercise 3: Observe accumulation
    ((w - 2) ** 2).backward()
    assert w.grad.item() == -8

    # Exercise 4: Clear gradient state
    w.grad = None
    ((w - 2) ** 2).backward()
    assert w.grad.item() == -4

    # Exercise 5: Inspect detachment
    detached = w.detach()
    assert detached.item() == 0 and detached.requires_grad is False

    # Exercise 6: Check an embedding table
    table = torch.tensor([[1.0, 0.0], [0.0, 1.0], [2.0, 2.0], [-1.0, 1.0]])
    embedding = nn.Embedding.from_pretrained(table, freeze=False)
    out = embedding(torch.tensor([2, 0, 2]))
    assert tuple(out.shape) == (3, 2)
    np.testing.assert_array_equal(out.detach().numpy(), [[2, 2], [1, 0], [2, 2]])
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
