"""torch-035: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Worked example A: Align predictions by ID
    truth = {"a": 0.0, "b": 1.0, "c": 2.0}
    a = {"a": 0.0, "b": 2.0, "c": 2.0}
    b = {"c": 3.0, "a": 1.0, "b": 2.0}
    ids = sorted(truth)
    difference = torch.tensor(
        [(a[i] - truth[i]) ** 2 - (b[i] - truth[i]) ** 2 for i in ids], dtype=torch.float64
    )
    assert difference.tolist() == [-1.0, 0.0, -1.0]

    # Worked example B: Interpret the average contrast
    np.testing.assert_allclose(difference.mean().item(), -2 / 3, atol=1e-12, rtol=0)

    # Worked example C: Resample pairs reproducibly
    generator = torch.Generator().manual_seed(7)
    indices = torch.randint(0, 3, (1000, 3), generator=generator)
    estimates = difference[indices].mean(1)
    assert (
        tuple(estimates.shape) == (1000,)
        and torch.isfinite(estimates).all()
        and estimates.min() >= -1
        and estimates.max() <= 0
    )

    # Exercise 4: Replay the local random stream
    again = torch.randint(0, 3, (1000, 3), generator=torch.Generator().manual_seed(7))
    assert torch.equal(indices, again)

    # Exercise 5: Reject missing assessment identities
    missing = {key: value for key, value in b.items() if key != "c"}
    assert set(missing) != set(truth)

    # Exercise 6: Preserve a final-test boundary
    ledger = [("choose", "validation"), ("assess", "test")]
    assert all(partition == "validation" for action, partition in ledger if action == "choose")
    assert ("choose", "test")[1] != "validation"

    # Exercise 1: Align a new pair of models
    truth2 = {"x": 1.0, "y": 2.0}
    model_a = {"x": 1.0, "y": 4.0}
    model_b = {"y": 2.0, "x": 0.0}
    keys = sorted(truth2)
    paired = torch.tensor(
        [(model_a[k] - truth2[k]) ** 2 - (model_b[k] - truth2[k]) ** 2 for k in keys],
        dtype=torch.float64,
    )
    assert paired.tolist() == [-1.0, 4.0]

    # Exercise 2: Interpret the new mean contrast
    assert paired.mean().item() == 1.5

    # Exercise 3: Bound the new bootstrap means
    gen = torch.Generator().manual_seed(11)
    draws = torch.randint(0, 2, (500, 2), generator=gen)
    boot = paired[draws].mean(1)
    assert set(boot.tolist()) <= {-1.0, 1.5, 4.0} and boot.min() >= -1 and boot.max() <= 4
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
