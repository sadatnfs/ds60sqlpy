"""torch-013: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Exercise 1: Convert fixed logits
    logits = torch.tensor([-2.0, 0.0, 2.0], dtype=torch.float64)
    probabilities = torch.sigmoid(logits)
    assert probabilities[1].item() == 0.5 and bool(torch.all(torch.diff(probabilities) > 0))

    # Exercise 2: Check the midpoint objective
    loss = F.binary_cross_entropy_with_logits(
        torch.tensor([0.0], dtype=torch.float64), torch.tensor([1.0], dtype=torch.float64)
    )
    np.testing.assert_allclose(loss.item(), np.log(2), atol=1e-12, rtol=0)

    # Exercise 3: Move the decision threshold
    assert (probabilities >= 0.5).tolist() == [False, True, True]
    assert (probabilities >= 0.8).tolist() == [False, False, True]

    # Exercise 4: Expose a double-sigmoid mistake
    wrong = F.binary_cross_entropy_with_logits(
        torch.tensor([0.5], dtype=torch.float64), torch.tensor([1.0], dtype=torch.float64)
    )
    assert abs(wrong.item() - np.log(2)) > 0.1

    # Exercise 5: Test extreme finite scores
    extreme = F.binary_cross_entropy_with_logits(
        torch.tensor([1000.0, -1000.0]), torch.tensor([1.0, 0.0]), reduction="none"
    )
    assert torch.isfinite(extreme).all()
    torch.testing.assert_close(extreme, torch.zeros(2), atol=1e-6, rtol=0)

    # Exercise 6: Count threshold errors
    truth = torch.tensor([False, True, True])
    assert (
        int(((probabilities >= 0.5) != truth).sum()) == 0
        and int(((probabilities >= 0.8) != truth).sum()) == 1
    )
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
