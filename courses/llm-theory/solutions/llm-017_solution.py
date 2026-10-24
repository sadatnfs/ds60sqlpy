"""llm-017: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Exercise 1: Shift the sequence
    ids = torch.tensor([[2, 5, 7, 3]])
    inputs = ids[:, :-1]
    targets = ids[:, 1:]
    assert inputs.tolist() == [[2, 5, 7]] and targets.tolist() == [[5, 7, 3]]

    # Exercise 2: Score uniform logits
    logits = torch.zeros((1, 3, 8))
    loss = F.cross_entropy(logits.reshape(-1, 8), targets.reshape(-1))
    np.testing.assert_allclose(loss.item(), np.log(8), atol=1e-6, rtol=0)

    # Exercise 3: Append ignored targets
    padded = torch.tensor([[5, 7, 3, -100, -100]])
    plogits = torch.zeros((1, 5, 8))
    new = F.cross_entropy(plogits.reshape(-1, 8), padded.reshape(-1), ignore_index=-100)
    assert int((padded != -100).sum()) == 3
    torch.testing.assert_close(new, loss, atol=1e-6, rtol=0)

    # Exercise 4: Expose the wrong denominator
    summed = F.cross_entropy(
        plogits.reshape(-1, 8), padded.reshape(-1), ignore_index=-100, reduction="sum"
    )
    wrong = summed / 5
    np.testing.assert_allclose(wrong.item(), 3 * np.log(8) / 5, atol=1e-6, rtol=0)
    assert wrong < loss

    # Exercise 5: Check gradient masking
    v = plogits.clone().requires_grad_()
    objective = F.cross_entropy(
        v.reshape(-1, 8), padded.reshape(-1), ignore_index=-100, reduction="sum"
    )
    objective.backward()
    assert torch.count_nonzero(v.grad[:, 3:]).item() == 0

    # Exercise 6: Reject all-padding batches
    empty = torch.tensor([[-100, -100]])
    active = int((empty != -100).sum())
    assert active == 0
    try:
        if active == 0:
            raise ValueError("no active targets")
    except ValueError:
        pass
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
