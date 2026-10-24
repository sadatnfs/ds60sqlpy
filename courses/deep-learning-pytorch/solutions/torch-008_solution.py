"""torch-008: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Exercise 1: Calculate the initial loss
    x = torch.tensor([1.0, 2.0, 3.0], dtype=torch.float64)
    y = 2 * x
    w = nn.Parameter(torch.tensor(0.0, dtype=torch.float64))
    loss = ((w * x - y) ** 2).mean()
    np.testing.assert_allclose(loss.item(), 56 / 3, atol=1e-12, rtol=0)

    # Exercise 2: Inspect the gradient before updating
    loss.backward()
    np.testing.assert_allclose(w.grad.item(), -56 / 3, atol=1e-12, rtol=0)
    assert w.item() == 0

    # Exercise 3: Apply exactly one SGD update
    optimizer = torch.optim.SGD([w], lr=0.1)
    optimizer.step()
    np.testing.assert_allclose(w.item(), 28 / 15, atol=1e-12, rtol=0)
    np.testing.assert_allclose(((w * x - y) ** 2).mean().item(), 56 / 675, atol=1e-12, rtol=0)

    # Exercise 4: Expose the broadcast counterexample
    wrong = nn.Parameter(torch.tensor(0.0, dtype=torch.float64))
    broken = ((wrong * x - y[:, None]) ** 2).mean()
    broken.backward()
    np.testing.assert_allclose(broken.item(), 56 / 3, atol=1e-12, rtol=0)
    assert wrong.grad.item() == -16

    # Exercise 5: Check a finite-difference gradient
    values = np.array([1.0, 2.0, 3.0])
    objective = lambda value: np.mean((value * values - 2 * values) ** 2)
    h = 0.001
    slope = (objective(h) - objective(-h)) / (2 * h)
    np.testing.assert_allclose(slope, -56 / 3, atol=1e-9, rtol=0)

    # Exercise 6: Clear the consumed gradient
    saved = w.item()
    optimizer.zero_grad(set_to_none=True)
    assert w.grad is None and w.item() == saved
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
