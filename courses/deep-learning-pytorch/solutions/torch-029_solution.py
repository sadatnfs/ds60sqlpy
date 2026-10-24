"""torch-029: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Exercise 1: Expose naive overflow
    logits = torch.tensor([1000.0, 999.0], dtype=torch.float32)
    naive = torch.exp(logits)
    assert torch.isinf(naive).all()

    # Exercise 2: Compute a stable class loss
    stable = F.cross_entropy(logits[None, :], torch.tensor([0]))
    np.testing.assert_allclose(stable.item(), np.log1p(np.exp(-1)), atol=1e-6, rtol=0)

    # Exercise 3: Check shift invariance
    torch.testing.assert_close(
        torch.softmax(logits, 0), torch.softmax(torch.tensor([0.0, -1.0]), 0), atol=1e-6, rtol=0
    )

    # Exercise 4: Inspect stable gradients
    values = logits.clone().requires_grad_()
    F.cross_entropy(values[None, :], torch.tensor([0])).backward()
    assert torch.isfinite(values.grad).all()
    np.testing.assert_allclose(values.grad.sum().item(), 0, atol=1e-6, rtol=0)

    # Exercise 5: Compare dtype ranges explicitly
    assert torch.finfo(torch.bfloat16).max > torch.finfo(torch.float16).max
    assert torch.finfo(torch.float32).eps > 0

    # Exercise 6: Reject a nonfinite input contract
    def checked_loss(value, target):
        if not bool(torch.isfinite(value).all()):
            raise ValueError("finite logits required")
        return F.cross_entropy(value, target)

    try:
        checked_loss(torch.tensor([[0.0, float("nan")]]), torch.tensor([0]))
    except ValueError:
        pass
    else:
        raise AssertionError("NaN logits accepted")
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
