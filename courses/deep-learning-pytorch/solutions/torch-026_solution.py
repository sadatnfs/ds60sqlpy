"""torch-026: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


class Residual(nn.Module):
    def __init__(self, width):
        super().__init__()
        self.width = width
        self.kernel = nn.Parameter(torch.zeros((width, width), dtype=torch.float64))
        self.register_buffer("scale", torch.tensor(1.0, dtype=torch.float64))

    def forward(self, x):
        if x.ndim != 2 or x.shape[1] != self.width:
            raise ValueError("feature width mismatch")
        return x + self.scale * (x @ self.kernel)


class Cube(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x):
        ctx.save_for_backward(x)
        return x**3

    @staticmethod
    def backward(ctx, grad_output):
        (x,) = ctx.saved_tensors
        return grad_output * 3 * x * x


def verify():
    # Exercise 1: Build an identity residual
    module = Residual(2)
    x = torch.tensor([[1.0, 2.0], [3.0, 4.0]], dtype=torch.float64)
    assert torch.equal(module(x), x)
    assert set(dict(module.named_parameters())) == {"kernel"} and set(
        dict(module.named_buffers())
    ) == {"scale"}

    # Exercise 2: Keep state stable across calls
    identity = id(module.kernel)
    module(torch.ones((1, 2), dtype=torch.float64))
    assert id(module.kernel) == identity and sum(p.numel() for p in module.parameters()) == 4

    # Exercise 3: Check a known residual transform
    with torch.no_grad():
        module.kernel.copy_(torch.eye(2, dtype=torch.float64))
        module.scale.fill_(0.5)
    torch.testing.assert_close(module(x), 1.5 * x, atol=1e-12, rtol=0)

    # Exercise 4: Reject incompatible feature width
    try:
        module(torch.ones((1, 3), dtype=torch.float64))
    except ValueError:
        pass
    else:
        raise AssertionError("incompatible residual accepted")

    # Exercise 5: Validate a custom cube derivative
    probe = torch.tensor([0.2, -0.7], dtype=torch.float64, requires_grad=True)
    assert torch.autograd.gradcheck(Cube.apply, (probe,), eps=1e-6, atol=1e-5, rtol=1e-3)

    # Exercise 6: Inspect the incoming-gradient factor
    value = torch.tensor([2.0], dtype=torch.float64, requires_grad=True)
    (2 * Cube.apply(value)).sum().backward()
    assert value.grad.item() == 24
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
