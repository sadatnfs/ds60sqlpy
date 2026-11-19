"""torch-004: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Worked example A: Compute residual reductions
    residual = torch.tensor([1.0, -1.0, 2.0], dtype=torch.float64)
    zero = torch.zeros_like(residual)
    assert F.mse_loss(residual, zero, reduction="sum").item() == 6
    assert F.mse_loss(residual, zero, reduction="mean").item() == 2
    torch.testing.assert_close(
        F.mse_loss(residual, zero, reduction="none"),
        torch.tensor([1.0, 1.0, 4.0], dtype=torch.float64),
    )

    # Worked example B: Duplicate the batch
    duplicated = residual.repeat(2)
    assert F.mse_loss(duplicated, torch.zeros_like(duplicated), reduction="sum").item() == 12
    assert F.mse_loss(duplicated, torch.zeros_like(duplicated), reduction="mean").item() == 2

    # Worked example C: Compare derivative scale
    a = residual.clone().requires_grad_()
    gsum = torch.autograd.grad((a * a).sum(), a)[0]
    b = residual.clone().requires_grad_()
    gmean = torch.autograd.grad((b * b).mean(), b)[0]
    torch.testing.assert_close(gsum, 3 * gmean, atol=1e-12, rtol=0)

    # Exercise 4: Inspect a feature denominator
    matrix = torch.ones((2, 2), dtype=torch.float64)
    assert F.mse_loss(matrix, torch.zeros_like(matrix)).item() == 1 and matrix.numel() == 4

    # Exercise 5: Mask numerator and denominator together
    losses = torch.tensor([1.0, 4.0, 100.0])
    mask = torch.tensor([True, True, False])
    valid = losses[mask].sum() / mask.sum()
    assert valid.item() == 2.5 and valid.item() != 5 / 3

    # Exercise 6: Separate a metric from the objective
    np.testing.assert_allclose(residual.abs().mean().item(), 4 / 3, atol=1e-12, rtol=0)
    assert residual.square().mean().item() == 2

    # Exercise 1: Reduce a new residual vector
    fresh = torch.tensor([3.0, 0.0, -1.0, 2.0], dtype=torch.float64)
    zeros = torch.zeros_like(fresh)
    assert (
        F.mse_loss(fresh, zeros, reduction="sum").item() == 14
        and F.mse_loss(fresh, zeros, reduction="mean").item() == 3.5
    )

    # Exercise 2: Predict the effect of an appended zero
    padded = torch.cat([fresh, torch.zeros(1, dtype=torch.float64)])
    assert F.mse_loss(padded, torch.zeros_like(padded), reduction="sum").item() == 14
    np.testing.assert_allclose(
        F.mse_loss(padded, torch.zeros_like(padded), reduction="mean").item(),
        2.8,
        atol=1e-12,
        rtol=0,
    )

    # Exercise 3: Compare gradient scale for four entries
    c = fresh.clone().requires_grad_()
    total_grad = torch.autograd.grad((c * c).sum(), c)[0]
    d = fresh.clone().requires_grad_()
    mean_grad = torch.autograd.grad((d * d).mean(), d)[0]
    torch.testing.assert_close(
        total_grad, torch.tensor([6.0, 0.0, -2.0, 4.0], dtype=torch.float64), atol=1e-12, rtol=0
    )
    torch.testing.assert_close(total_grad, 4 * mean_grad, atol=1e-12, rtol=0)
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
