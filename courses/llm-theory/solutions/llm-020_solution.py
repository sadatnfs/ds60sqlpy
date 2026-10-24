"""llm-020: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Exercise 1: Measure a small linear layer
    x = torch.tensor([[1.0, -1.0, 2.0, -2.0]])
    small = 0.01 * torch.eye(4)
    out = x @ small
    np.testing.assert_allclose(
        torch.linalg.vector_norm(out).item(), 0.01 * np.sqrt(10), atol=1e-6, rtol=0
    )

    # Exercise 2: Increase only the scale
    large = 100 * torch.eye(4)
    bigger = x @ large
    np.testing.assert_allclose(
        (torch.linalg.vector_norm(bigger) / torch.linalg.vector_norm(out)).item(),
        10000,
        atol=0.01,
        rtol=0,
    )

    # Exercise 3: Trace gradients
    norms = []
    for initial in [small, large]:
        w = initial.clone().requires_grad_()
        loss = (x @ w).square().mean()
        loss.backward()
        norms.append(w.grad.norm().item())
    assert np.isfinite(norms).all() and norms[1] > norms[0]

    # Exercise 4: Find the first overflow
    extreme = x @ (torch.eye(4) * 1e38)
    objective = extreme.square().mean()
    assert not torch.isfinite(objective)

    # Exercise 5: Repair on the same input
    repaired = x @ small
    assert torch.isfinite(repaired).all() and torch.isfinite(repaired.square().mean())

    # Exercise 6: Check residual dimensions
    assert tuple((x + x @ small).shape) == (1, 4)
    try:
        x + torch.ones((1, 3))
    except RuntimeError:
        pass
    else:
        raise AssertionError("incompatible residual accepted")
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
