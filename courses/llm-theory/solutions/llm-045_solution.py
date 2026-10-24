"""llm-045: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def rms_norm(x, eps=1e-8):
    return x / torch.sqrt(x.square().mean(-1, keepdim=True) + eps)


def layer_norm(x, eps=1e-8):
    centered = x - x.mean(-1, keepdim=True)
    return centered / torch.sqrt(centered.square().mean(-1, keepdim=True) + eps)


def verify():
    # Exercise 1: Compare RMSNorm andLayerNorm
    x = torch.tensor([3.0, 4.0], dtype=torch.float64)
    rms = rms_norm(x)
    centered = layer_norm(x)
    assert abs(rms.mean().item()) > 0.5
    np.testing.assert_allclose(centered.mean().item(), 0, atol=1e-12, rtol=0)
    np.testing.assert_allclose(
        rms.detach().numpy(), np.array([3.0, 4.0]) / np.sqrt(12.5 + 1e-8), atol=1e-12, rtol=0
    )

    # Exercise 2: Trace pre/post residual Jacobians
    value = torch.tensor([1.0, 2.0, 4.0], dtype=torch.float64, requires_grad=True)
    pre = torch.autograd.functional.jacobian(lambda z: z + 0 * layer_norm(z), value)
    post = torch.autograd.functional.jacobian(lambda z: layer_norm(z + 0 * z), value)
    torch.testing.assert_close(pre, torch.eye(3, dtype=torch.float64), atol=1e-12, rtol=0)
    torch.testing.assert_close(
        post @ torch.ones(3, dtype=torch.float64),
        torch.zeros(3, dtype=torch.float64),
        atol=1e-10,
        rtol=0,
    )

    # Exercise 3: Calculate a SwiGLU gate derivative
    gate = torch.tensor(0.0, dtype=torch.float64, requires_grad=True)
    up = torch.tensor(2.0, dtype=torch.float64, requires_grad=True)
    output = F.silu(gate) * up
    output.backward()
    assert output.item() == 0 and gate.grad.item() == 1 and up.grad.item() == 0

    # Exercise 4: Check the RMSNorm Jacobian formula
    value = torch.tensor([1.0, 2.0, 3.0], dtype=torch.float64, requires_grad=True)
    r = torch.sqrt(value.square().mean() + 1e-8)
    width = value.numel()
    analytic = torch.eye(width, dtype=torch.float64) / r - torch.outer(value, value) / (
        width * r**3
    )
    automatic = torch.autograd.functional.jacobian(rms_norm, value)
    torch.testing.assert_close(automatic, analytic, atol=1e-10, rtol=0)

    # Exercise 5: Match feed-forward parameter budgets
    d = 4
    plain_hidden = 6
    gated_hidden = 4
    assert 2 * d * plain_hidden == 3 * d * gated_hidden == 48
    inputs = torch.tensor([[1.0, 0.0, -1.0, 2.0], [0.0, 1.0, 2.0, -1.0]], dtype=torch.float64)
    wg = torch.eye(4, dtype=torch.float64)
    wu = 2 * wg
    wd = 0.5 * wg
    result = (F.silu(inputs @ wg) * (inputs @ wu)) @ wd
    assert tuple(result.shape) == (2, 4) and torch.isfinite(result).all()

    # Exercise 6: Test invariance andzero-vector boundaries
    base = torch.tensor([1.0, 2.0, 3.0], dtype=torch.float64)
    torch.testing.assert_close(layer_norm(base + 5), layer_norm(base), atol=1e-12, rtol=0)
    assert not torch.allclose(rms_norm(base + 5), rms_norm(base))
    assert torch.isfinite(rms_norm(torch.zeros(3, dtype=torch.float64))).all()
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
