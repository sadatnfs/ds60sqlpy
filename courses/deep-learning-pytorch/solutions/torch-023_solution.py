"""torch-023: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Exercise 1: Expose detachment
    w = nn.Parameter(torch.tensor(0.0, dtype=torch.float64))
    disconnected = ((w - 2) ** 2).detach()
    assert not disconnected.requires_grad
    try:
        disconnected.backward()
    except RuntimeError:
        pass
    else:
        raise AssertionError("detached loss backpropagated")

    # Exercise 2: Repair two exact updates
    x = torch.tensor([1.0, 2.0, 3.0], dtype=torch.float64)
    y = 2 * x
    optimizer = torch.optim.SGD([w], lr=0.1)
    history = []
    for _ in range(2):
        optimizer.zero_grad(set_to_none=True)
        loss = ((w * x - y) ** 2).mean()
        loss.backward()
        assert w.grad is not None
        optimizer.step()
        history.append(w.item())
    np.testing.assert_allclose(history, [28 / 15, 448 / 225], atol=1e-12, rtol=0)

    # Exercise 3: Inspect norm clipping
    parameter = nn.Parameter(torch.zeros(2))
    parameter.grad = torch.tensor([3.0, 4.0])
    before = torch.nn.utils.clip_grad_norm_([parameter], 1.0)
    assert before.item() == 5
    torch.testing.assert_close(parameter.grad, torch.tensor([0.6, 0.8]), atol=1e-6, rtol=0)

    # Exercise 4: Apply the clipped update
    torch.optim.SGD([parameter], lr=0.1).step()
    torch.testing.assert_close(parameter.detach(), torch.tensor([-0.06, -0.08]), atol=1e-6, rtol=0)

    # Exercise 5: Reject nonfinite gradient norms
    bad = nn.Parameter(torch.zeros(1))
    bad.grad = torch.tensor([float("inf")])
    try:
        torch.nn.utils.clip_grad_norm_([bad], 1.0, error_if_nonfinite=True)
    except RuntimeError:
        pass
    else:
        raise AssertionError("nonfinite gradient accepted")

    # Exercise 6: Recompute post-update loss
    after = ((w * x - y) ** 2).mean().item()
    assert 0 <= after < 56 / 675
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
