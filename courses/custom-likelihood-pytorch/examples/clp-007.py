"""Complete float64 CPU likelihood investigation with original synthetic data."""

from __future__ import annotations

import json

import torch

DTYPE = torch.float64
torch.set_num_threads(1)


def tensor(values):
    return torch.as_tensor(values, dtype=DTYPE)


def logistic_nll(beta, design, y):
    if (
        design.ndim != 2
        or beta.ndim != 1
        or y.shape != (design.shape[0],)
        or beta.shape != (design.shape[1],)
    ):
        raise ValueError("Match row, feature and coefficient dimensions")
    if not bool(torch.all((y == 0) | (y == 1))):
        raise ValueError("Binary observations must be zero or one")
    if not len(y) or not all(bool(torch.isfinite(value).all()) for value in (beta, design, y)):
        raise ValueError("Use finite coefficients and a nonempty finite sample")
    logits = design @ beta
    return (torch.nn.functional.softplus(logits) - y * logits).sum()


def fit_overlap(design, y):
    beta = torch.zeros(design.shape[1], dtype=DTYPE, requires_grad=True)
    optimizer = torch.optim.LBFGS(
        [beta],
        max_iter=70,
        tolerance_grad=1e-10,
        tolerance_change=1e-13,
        line_search_fn="strong_wolfe",
    )

    def closure():
        optimizer.zero_grad()
        loss = logistic_nll(beta, design, y)
        loss.backward()
        return loss

    optimizer.step(closure)
    gradient = torch.autograd.grad(logistic_nll(beta, design, y), beta)[0]
    return beta.detach(), float(gradient.abs().max())


def run_cases():
    x, y = tensor([-2, -1, 0, 1, 2, 3]), tensor([0, 1, 0, 1, 1, 0])
    design = torch.stack([torch.ones_like(x), x], dim=1)
    trial = tensor([0.2, -0.3]).requires_grad_()
    gradient = torch.autograd.grad(logistic_nll(trial, design, y), trial)[0]
    analytic = design.T @ (torch.sigmoid(design @ trial.detach()) - y)
    assert torch.allclose(gradient, analytic, atol=1e-12, rtol=0)
    beta, norm = fit_overlap(design, y)
    assert norm < 1e-6
    separated = tensor([-2, -1, 1, 2]).reshape(-1, 1)
    labels = tensor([0, 0, 1, 1])
    losses = [float(logistic_nll(tensor([slope]), separated, labels)) for slope in (1, 2, 4, 8)]
    assert all(a > b for a, b in zip(losses[:-1], losses[1:], strict=True))
    huge = logistic_nll(tensor([1000.0]), tensor([[1.0], [-1.0]]), tensor([1, 0]))
    assert torch.isfinite(huge)
    return {
        "overlap_coefficients": beta.tolist(),
        "gradient_max_abs": norm,
        "probabilities": torch.sigmoid(design @ beta).tolist(),
        "separated_slope_path_nll": losses,
        "separated_finite_mle": False,
        "extreme_stable_nll": float(huge),
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
