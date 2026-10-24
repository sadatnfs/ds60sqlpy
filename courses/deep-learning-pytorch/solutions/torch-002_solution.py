"""torch-002: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Exercise 1: Inspect shape and stride
    x = torch.arange(6, dtype=torch.float64, device="cpu").reshape(2, 3)
    assert (
        tuple(x.shape) == (2, 3)
        and x.stride() == (3, 1)
        and x.device.type == "cpu"
        and x.dtype == torch.float64
    )

    # Exercise 2: Expose shared storage
    row = x[0]
    row[0] = 99
    assert x[0, 0].item() == 99

    # Exercise 3: Create an independent copy
    owned = x.clone()
    owned[0, 0] = -1
    assert owned[0, 0].item() == -1 and x[0, 0].item() == 99

    # Exercise 4: Trace a transposed layout
    transposed = x.T
    assert (
        tuple(transposed.shape) == (3, 2)
        and transposed.stride() == (1, 3)
        and not transposed.is_contiguous()
    )
    assert transposed.contiguous().is_contiguous()

    # Exercise 5: Detect a pairing broadcast
    v = torch.tensor([1.0, 2.0, 3.0])
    column = v[:, None]
    assert tuple((v - column).shape) == (3, 3) and tuple((v - v).shape) == (3,)

    # Exercise 6: Reject incompatible arithmetic
    try:
        torch.zeros((2, 3)) + torch.zeros(4)
    except RuntimeError:
        pass
    else:
        raise AssertionError("incompatible shapes accepted")
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
