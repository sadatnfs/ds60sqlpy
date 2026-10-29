"""Complete float64 CPU likelihood investigation with original synthetic data."""

from __future__ import annotations

import json
import math

import torch

DTYPE = torch.float64
torch.set_num_threads(1)


def tensor(values):
    return torch.as_tensor(values, dtype=DTYPE)


def mean_curve(raw, time):
    return raw[0].exp() * torch.exp(-raw[1].exp() * time) + raw[2]


def covariance(length, sigma, rho):
    if length < 1 or not math.isfinite(sigma) or sigma <= 0 or not -1 < rho < 1:
        raise ValueError("Require a positive finite scale and stationary correlation")
    index = torch.arange(length)
    return sigma**2 * tensor(rho).pow((index[:, None] - index[None, :]).abs())


def panel_nll(raw, time, y, scale=0.25, rho=0.5):
    if raw.shape != (3,) or time.ndim != 1 or y.ndim != 2 or y.shape[1] != len(time):
        raise ValueError("Use three parameters and complete panels aligned to observation times")
    if y.numel() == 0 or not all(bool(torch.isfinite(value).all()) for value in (raw, time, y)):
        raise ValueError("Use finite parameters, times and nonempty panel data")
    factor = torch.linalg.cholesky(covariance(len(time), scale, rho))
    residual = y - mean_curve(raw, time)
    whitened = torch.linalg.solve_triangular(factor, residual.T, upper=False)
    return (
        y.shape[0] * (len(time) * math.log(2 * math.pi) / 2 + torch.log(torch.diag(factor)).sum())
        + whitened.square().sum() / 2
    )


def fit_panel(time, y, rho):
    raw = tensor([math.log(1.8), math.log(0.3), 0.3]).requires_grad_()
    optimizer = torch.optim.LBFGS(
        [raw],
        max_iter=160,
        tolerance_grad=1e-10,
        tolerance_change=1e-14,
        line_search_fn="strong_wolfe",
    )
    calls = 0

    def closure():
        nonlocal calls
        calls += 1
        optimizer.zero_grad()
        loss = panel_nll(raw, time, y, rho=rho)
        loss.backward()
        return loss

    optimizer.step(closure)

    def objective(value):
        return panel_nll(value, time, y, rho=rho)

    gradient = torch.autograd.grad(objective(raw), raw)[0]
    hessian = torch.autograd.functional.hessian(objective, raw)
    eigen = torch.linalg.eigvalsh(hessian)
    if float(eigen[0]) <= 0:
        raise ValueError("Nonpositive observed information cannot support this delta-method report")
    return (
        raw.detach(),
        torch.linalg.inv(hessian),
        float(gradient.abs().max()),
        calls,
        float(eigen[0]),
    )


def run_cases():
    time = torch.arange(6, dtype=DTYPE)
    truth = tensor([math.log(2.5), math.log(0.55), 0.6])
    residual = tensor([0.12, -0.08, 0.06, 0.04, -0.10, 0.09])
    y = mean_curve(truth, time) + torch.stack([residual, -residual, torch.zeros_like(residual)])
    estimate, parameter_covariance, gradient, calls, minimum_information = fit_panel(time, y, 0.5)
    iid, _, _, _, _ = fit_panel(time, y, 0.0)
    assert torch.allclose(estimate, truth, atol=5e-5, rtol=0) and gradient < 5e-4
    assert torch.allclose(iid, truth, atol=5e-5, rtol=0)
    horizon = tensor([1, 2])
    future_time = time[-1] + horizon
    mean = mean_curve(estimate, future_time)
    last_residual = y[:, -1] - mean_curve(estimate, time)[-1]
    conditional = mean + last_residual[:, None] * tensor(0.5).pow(horizon)
    future_noise = tensor([[0.05, -0.03], [-0.02, 0.04], [0.01, -0.02]])
    heldout = (
        mean_curve(truth, future_time)
        + tensor([0.09, -0.09, 0])[:, None] * tensor(0.5).pow(horizon)
        + future_noise
    )
    jacobian = torch.autograd.functional.jacobian(lambda p: mean_curve(p, future_time), estimate)
    mean_variance = torch.einsum("ij,jk,ik->i", jacobian, parameter_covariance, jacobian)
    plug_in_observation_variance = mean_variance + 0.25**2 * (1 - tensor(0.5).pow(2 * horizon))
    assert bool(torch.isfinite(conditional).all()) and bool(
        (plug_in_observation_variance > 0).all()
    )
    return {
        "parameters": [float(estimate[0].exp()), float(estimate[1].exp()), float(estimate[2])],
        "train_nll": float(panel_nll(estimate, time, y)),
        "gradient_max_abs": gradient,
        "objective_evaluations": calls,
        "minimum_information_eigenvalue": minimum_information,
        "future_times": future_time.tolist(),
        "conditional_group_forecasts": conditional.tolist(),
        "mean_forecast_se": mean_variance.sqrt().tolist(),
        "plug_in_observation_sd": plug_in_observation_variance.sqrt().tolist(),
        "conditional_rmse": float(torch.mean((conditional - heldout).square()).sqrt()),
        "wrong_independence_rmse": float(torch.mean((mean[None, :] - heldout).square()).sqrt()),
        "scope": (
            "three deliberately symmetric synthetic panels; "
            "supplied covariance; CPU numerical demonstration"
        ),
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
