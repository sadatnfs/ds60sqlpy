"""Complete float64 CPU likelihood investigation with original synthetic data."""

from __future__ import annotations

import json
import math

import torch

DTYPE = torch.float64
torch.set_num_threads(1)


def tensor(values):
    return torch.as_tensor(values, dtype=DTYPE)


def mean_curve(theta, time):
    return theta[0] * torch.exp(-theta[1] * time) + theta[2]


def prediction_components(theta, covariance, time, observation_variance, new_group_variance):
    if observation_variance < 0 or new_group_variance < 0:
        raise ValueError("Variance components must be nonnegative")
    gradient = torch.autograd.functional.jacobian(lambda p: mean_curve(p, time), theta)
    mean_variance = torch.einsum("ij,jk,ik->i", gradient, covariance, gradient)
    if bool((mean_variance < 0).any()):
        raise ValueError("Parameter covariance implies negative forecast variance")
    return (
        mean_variance,
        mean_variance + observation_variance,
        mean_variance + observation_variance + new_group_variance,
    )


def run_cases():
    theta = tensor([2.4, 0.65, 0.7])
    covariance = torch.diag(tensor([0.04, 0.0025, 0.01]))
    time = tensor([0, 2, 6])
    vm, vo, vg = prediction_components(theta, covariance, time, 0.09, 0.16)
    assert bool(torch.all(vm < vo) & torch.all(vo < vg))
    gradient = torch.autograd.functional.jacobian(lambda p: mean_curve(p, time), theta)
    analytic = torch.stack(
        [
            torch.exp(-theta[1] * time),
            -theta[0] * time * torch.exp(-theta[1] * time),
            torch.ones_like(time),
        ],
        dim=1,
    )
    assert torch.allclose(gradient, analytic)
    mean = mean_curve(theta, time)
    rows = [
        {
            "time": float(t),
            "mean": float(m),
            "mean_se": float(a.sqrt()),
            "observation_sd": float(b.sqrt()),
            "new_group_sd": float(c.sqrt()),
        }
        for t, m, a, b, c in zip(time, mean, vm, vo, vg, strict=True)
    ]
    latent_mean, latent_variance = 0.4, 0.36
    median = math.exp(latent_mean)
    expectation = math.exp(latent_mean + latent_variance / 2)
    assert expectation > median
    return {
        "forecast_components": rows,
        "lognormal_median": median,
        "lognormal_mean": expectation,
        "interval_multiplier": 1.96,
        "covariance_is_supplied_for_delta_method_demonstration": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
