"""Complete float64 CPU likelihood investigation with original synthetic data."""

from __future__ import annotations

import json
import math

import torch

DTYPE = torch.float64
torch.set_num_threads(1)


def tensor(values):
    return torch.as_tensor(values, dtype=DTYPE)


def heteroskedastic_nll(theta, z, y):
    if theta.shape != (3,) or z.ndim != 1 or y.shape != z.shape or not len(y):
        raise ValueError("Use three parameters and matching nonempty covariate/response vectors")
    if not all(bool(torch.isfinite(value).all()) for value in (theta, z, y)):
        raise ValueError("Parameters, scale covariate and observations must be finite")
    mean = theta[0]
    log_sigma = theta[1] + theta[2] * z
    return (
        log_sigma
        + 0.5 * math.log(2 * math.pi)
        + (y - mean).square() * torch.exp(-2 * log_sigma) / 2
    ).sum()


def fit_scales(z, y):
    theta = tensor([0.3, 0.2, 0.2]).requires_grad_()
    optimizer = torch.optim.LBFGS(
        [theta],
        max_iter=100,
        tolerance_grad=1e-10,
        tolerance_change=1e-14,
        line_search_fn="strong_wolfe",
    )

    def closure():
        optimizer.zero_grad()
        value = heteroskedastic_nll(theta, z, y)
        value.backward()
        return value

    optimizer.step(closure)
    gradient = torch.autograd.grad(heteroskedastic_nll(theta, z, y), theta)[0]
    return theta.detach(), float(gradient.abs().max())


def run_cases():
    z = tensor([0, 0, 0, 0, 1, 1, 1, 1])
    y = tensor([-1, 1, -1, 1, -3, 3, -3, 3])
    theta, gradient = fit_scales(z, y)
    assert torch.allclose(theta, tensor([0, 0, math.log(3)]), atol=2e-6, rtol=0)
    log_sigma = theta[1] + theta[2] * z
    residual_only = [
        float(((y - theta[0]).square() * torch.exp(-2 * (log_sigma + shift)) / 2).sum())
        for shift in (0, 2)
    ]
    proper = [float(heteroskedastic_nll(theta + tensor([0, shift, 0]), z, y)) for shift in (0, 2)]
    assert residual_only[1] < residual_only[0] and proper[1] > proper[0]
    standardized = (y - theta[0]) / log_sigma.exp()
    assert torch.allclose(
        standardized.square().reshape(2, 4).mean(1), tensor([1, 1]), atol=2e-6, rtol=0
    )
    return {
        "parameters": theta.tolist(),
        "group_scales": [float(theta[1].exp()), float((theta[1] + theta[2]).exp())],
        "gradient_max_abs": gradient,
        "residual_only_inflation_path": residual_only,
        "proper_nll_inflation_path": proper,
        "fixture": "symmetric synthetic residuals provide an exact scale oracle",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
