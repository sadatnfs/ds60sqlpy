"""torch-006: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Exercise 1: Trace the chain rule
    w = torch.tensor(1.0, dtype=torch.float64, requires_grad=True)
    z = 2 * w
    a = z * z
    loss = (a - 1) ** 2
    gradient = torch.autograd.grad(loss, w)[0]
    assert (z.item(), a.item(), loss.item(), gradient.item()) == (2.0, 4.0, 9.0, 48.0)

    # Exercise 2: Check an independent slope
    h = 1e-5
    f = lambda value: ((2 * value) ** 2 - 1) ** 2
    numeric = (f(1 + h) - f(1 - h)) / (2 * h)
    np.testing.assert_allclose(numeric, 48, atol=1e-5, rtol=0)

    # Exercise 3: Observe a leaf mutation guard
    leaf = torch.tensor(1.0, requires_grad=True)
    try:
        leaf.add_(1)
    except RuntimeError:
        pass
    else:
        raise AssertionError("unsafe leaf mutation accepted")

    # Exercise 4: Expose saved-value invalidation
    value = torch.tensor(2.0, requires_grad=True)
    objective = value.square()
    with torch.no_grad():
        value.add_(1)
    try:
        objective.backward()
    except RuntimeError:
        pass
    else:
        raise AssertionError("stale saved value accepted")

    # Exercise 5: Inspect a ReLU convention
    points = torch.tensor([-1.0, 0.0, 1.0], requires_grad=True)
    torch.relu(points).sum().backward()
    torch.testing.assert_close(points.grad, torch.tensor([0.0, 0.0, 1.0]))

    # Exercise 6: Recompute after an update
    parameter = torch.tensor(1.0, dtype=torch.float64, requires_grad=True)
    with torch.no_grad():
        parameter.add_(0.5)
    fresh = (parameter - 2) ** 2
    assert torch.autograd.grad(fresh, parameter)[0].item() == -1
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
