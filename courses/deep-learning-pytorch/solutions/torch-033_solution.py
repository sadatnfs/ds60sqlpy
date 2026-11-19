"""torch-033: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

MODEL = nn.Linear(2, 1, bias=False)
with torch.no_grad():
    MODEL.weight.copy_(torch.tensor([[2.0, -1.0]]))


def predict(x):
    if not isinstance(x, torch.Tensor) or x.dtype != torch.float32:
        raise TypeError("float32 tensor required")
    if x.device.type != "cpu":
        raise ValueError("CPU input required")
    if x.ndim != 2 or x.shape[1] != 2:
        raise ValueError("shape must be (batch,2)")
    if not 1 <= len(x) <= 4:
        raise ValueError("batch limit1..4")
    if not bool(torch.isfinite(x).all()):
        raise ValueError("finite input required")
    MODEL.eval()
    with torch.inference_mode():
        output = MODEL(x).squeeze(-1)
    return output.clone()


def verify():
    # Worked example A: Predict a valid batch
    x = torch.tensor([[1.0, 2.0], [3.0, 4.0]], dtype=torch.float32)
    result = predict(x)
    assert (
        result.tolist() == [0.0, 2.0] and tuple(result.shape) == (2,) and not result.requires_grad
    )

    # Worked example B: Check per-record batching parity
    single = torch.cat([predict(x[i : i + 1]) for i in range(len(x))])
    torch.testing.assert_close(single, result, atol=0, rtol=0)

    # Worked example C: Reject empty and oversized batches
    for bad in [torch.empty((0, 2)), torch.zeros((5, 2))]:
        try:
            predict(bad)
        except ValueError as error:
            assert "batch" in str(error)
        else:
            raise AssertionError("invalid batch accepted")

    # Exercise 4: Reject shape and dtype ambiguity
    for bad, kind in [
        (torch.tensor([1.0, 2.0]), ValueError),
        (torch.zeros((2, 3)), ValueError),
        (torch.ones((1, 2), dtype=torch.int64), TypeError),
    ]:
        try:
            predict(bad)
        except kind:
            pass
        else:
            raise AssertionError("input contract bypassed")

    # Exercise 5: Reject nonfinite values
    try:
        predict(torch.tensor([[float("nan"), 1.0]]))
    except ValueError as error:
        assert "finite" in str(error)
    else:
        raise AssertionError("NaN accepted")

    # Exercise 6: Preserve caller data
    saved = x.clone()
    output = predict(x)
    output[0] = 999
    assert torch.equal(x, saved)

    # Exercise 1: Predict a new valid batch
    rows = torch.tensor([[0.0, 1.0], [2.0, 0.0], [1.0, 1.0]])
    assert predict(rows).tolist() == [-1.0, 4.0, 1.0]

    # Exercise 2: Check the batch boundary
    assert tuple(predict(torch.ones((4, 2))).shape) == (4,)
    try:
        predict(torch.ones((5, 2)))
    except ValueError:
        pass
    else:
        raise AssertionError("oversized batch accepted")

    # Exercise 3: Reject a float64 batch
    try:
        predict(rows.double())
    except TypeError:
        pass
    else:
        raise AssertionError("float64 accepted")
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
