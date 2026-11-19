"""torch-002: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Worked example A: Inspect shape and stride
    x = torch.arange(6, dtype=torch.float64, device="cpu").reshape(2, 3)
    assert (
        tuple(x.shape) == (2, 3)
        and x.stride() == (3, 1)
        and x.device.type == "cpu"
        and x.dtype == torch.float64
    )

    # Worked example B: Expose shared storage
    row = x[0]
    row[0] = 99
    assert x[0, 0].item() == 99

    # Worked example C: Create an independent copy
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

    # Exercise 1: Predict a 3-by-2 layout
    grid = torch.arange(6, dtype=torch.float32).reshape(3, 2)
    assert (
        tuple(grid.shape) == (3, 2)
        and grid.stride() == (2, 1)
        and grid.dtype == torch.float32
        and grid.device.type == "cpu"
    )

    # Exercise 2: Write through a column view
    column = grid[:, 1]
    column[2] = -7
    assert grid[2, 1].item() == -7 and column.stride() == (2,)

    # Exercise 3: Separate contiguous from clone
    same = grid.contiguous()
    owned = grid.clone()
    same[0, 0] = 100
    owned[0, 0] = -100
    assert (
        same.data_ptr() == grid.data_ptr()
        and grid[0, 0].item() == 100
        and owned[0, 0].item() == -100
    )
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
