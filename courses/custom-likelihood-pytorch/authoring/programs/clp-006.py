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
    amplitude, rate = torch.exp(raw[:2])
    return amplitude * torch.exp(-rate * time) + raw[2]


def fit_decay(time, y, sigma=0.2):
    raw = tensor([math.log(1.0), math.log(0.3), 0.0]).requires_grad_()
    optimizer = torch.optim.LBFGS(
        [raw],
        max_iter=150,
        tolerance_grad=1e-10,
        tolerance_change=1e-14,
        line_search_fn="strong_wolfe",
    )

    def objective(value):
        return ((y - mean_curve(value, time)).square() / (2 * sigma**2)).sum()

    def closure():
        optimizer.zero_grad()
        loss = objective(raw)
        loss.backward()
        return loss

    optimizer.step(closure)
    gradient = torch.autograd.grad(objective(raw), raw)[0]
    return raw.detach(), float(gradient.abs().max())


def sensitivity_condition(raw, time):
    jacobian = torch.autograd.functional.jacobian(lambda value: mean_curve(value, time), raw)
    singular = torch.linalg.svdvals(jacobian)
    return float(singular[0] / singular[-1])


def run_cases():
    truth = tensor([math.log(2.4), math.log(0.65), 0.7])
    time = torch.linspace(0, 6, 25, dtype=DTYPE)
    y = mean_curve(truth, time)
    estimate, gradient = fit_decay(time, y)
    assert torch.allclose(estimate, truth, atol=3e-5, rtol=0)
    long_condition = sensitivity_condition(truth, time)
    short_condition = sensitivity_condition(truth, torch.linspace(0, 0.08, 25, dtype=DTYPE))
    assert short_condition > 100 * long_condition
    future = mean_curve(estimate, tensor([7, 9]))
    assert torch.isfinite(future).all() and gradient < 1e-4
    return {
        "physical_parameters": [
            float(estimate[0].exp()),
            float(estimate[1].exp()),
            float(estimate[2]),
        ],
        "gradient_max_abs": gradient,
        "long_window_condition": long_condition,
        "short_window_condition": short_condition,
        "future_mean": future.tolist(),
        "fixture": "noiseless optimization oracle with fixed scale, not empirical uncertainty",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
