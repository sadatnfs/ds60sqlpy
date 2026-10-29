"""Complete float64 CPU likelihood investigation with original synthetic data."""

from __future__ import annotations

import json
from itertools import product

import torch

DTYPE = torch.float64
torch.set_num_threads(1)


def tensor(values):
    return torch.as_tensor(values, dtype=DTYPE)


def inverse_information(hessian):
    if (
        hessian.ndim != 2
        or hessian.shape[0] != hessian.shape[1]
        or not torch.allclose(hessian, hessian.T)
    ):
        raise ValueError("Observed information must be square and symmetric")
    eigen = torch.linalg.eigvalsh(hessian)
    if not bool(torch.isfinite(eigen).all()) or float(eigen[0]) <= 1e-10:
        raise ValueError("Weak or nonpositive information: inverse-Hessian interval withheld")
    return torch.linalg.inv(hessian)


def exact_cluster_bootstrap(cluster_means):
    groups = len(cluster_means)
    if not 2 <= groups <= 5:
        raise ValueError("Keep this exact enumeration between two and five clusters")
    return torch.stack(
        [cluster_means[list(indices)].mean() for indices in product(range(groups), repeat=groups)]
    )


def run_cases():
    y = tensor([[0, 0], [2, 2], [4, 4], [6, 6]])
    mu = y.mean()
    n = y.numel()
    residual = y - mu
    model_variance = 1 / n
    iid_sandwich = float(residual.square().sum() / n**2)
    clustered_sandwich = float(residual.sum(dim=1).square().sum() / n**2)
    bootstrap = exact_cluster_bootstrap(y.mean(dim=1))
    bootstrap_variance = float(bootstrap.var(unbiased=False))
    assert abs(iid_sandwich - 0.625) < 1e-12
    assert abs(clustered_sandwich - 1.25) < 1e-12 and abs(bootstrap_variance - 1.25) < 1e-12
    weak_rejected = False
    try:
        inverse_information(tensor([[1, 1], [1, 1]]))
    except ValueError:
        weak_rejected = True
    assert weak_rejected
    return {
        "mean": float(mu),
        "working_model_variance": model_variance,
        "iid_sandwich_variance": iid_sandwich,
        "cluster_sandwich_variance_uncorrected": clustered_sandwich,
        "exact_cluster_bootstrap_variance": bootstrap_variance,
        "bootstrap_percentile_interval": torch.quantile(bootstrap, tensor([0.025, 0.975])).tolist(),
        "bootstrap_resamples": len(bootstrap),
        "weak_information_rejected": weak_rejected,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
