"""torch-003: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Exercise 1: Calculate a known affine layer
    layer = nn.Linear(3, 1, bias=True, dtype=torch.float64)
    with torch.no_grad():
        layer.weight.copy_(torch.tensor([[1.0, 0.0, -1.0]], dtype=torch.float64))
        layer.bias.fill_(2.0)
    x = torch.tensor([[1.0, 2.0, 3.0], [0.0, 1.0, 0.0]], dtype=torch.float64)
    out = layer(x)
    torch.testing.assert_close(
        out, torch.tensor([[0.0], [2.0]], dtype=torch.float64), atol=1e-12, rtol=0
    )

    # Exercise 2: Inspect registered state
    assert sum(p.numel() for p in layer.parameters()) == 4
    assert set(layer.state_dict()) == {"weight", "bias"}

    # Exercise 3: Compare with a mathematical matrix
    mathematical_w = layer.weight.T
    assert tuple(mathematical_w.shape) == (3, 1)
    torch.testing.assert_close(x @ mathematical_w + layer.bias, out, atol=1e-12, rtol=0)

    # Exercise 4: Remove the intercept explicitly
    no_bias = nn.Linear(3, 1, bias=False, dtype=torch.float64)
    with torch.no_grad():
        no_bias.weight.copy_(layer.weight)
    assert sum(p.numel() for p in no_bias.parameters()) == 3
    torch.testing.assert_close(
        no_bias(x), torch.tensor([[-2.0], [0.0]], dtype=torch.float64), atol=1e-12, rtol=0
    )

    # Exercise 5: Expose an unregistered tensor
    plain = nn.Module()
    plain.weight = torch.tensor([1.0], requires_grad=True)
    proper = nn.Module()
    proper.weight = nn.Parameter(torch.tensor([1.0]))
    assert len(list(plain.parameters())) == 0 and len(list(proper.parameters())) == 1

    # Exercise 6: Reject wrong feature width
    try:
        layer(torch.ones((1, 2), dtype=torch.float64))
    except RuntimeError:
        pass
    else:
        raise AssertionError("wrong feature width accepted")
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
