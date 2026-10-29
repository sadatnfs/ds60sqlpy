"""Complete float64 CPU likelihood investigation with original synthetic data."""

from __future__ import annotations

import json

import torch

DTYPE = torch.float64
torch.set_num_threads(1)


def tensor(values):
    return torch.as_tensor(values, dtype=DTYPE)


def audited_loss(theta, design, y):
    if theta.shape != (design.shape[1],) or not bool(torch.isfinite(theta).all()):
        raise ValueError("Use one finite coefficient per design column")
    return (design @ theta - y).square().sum() / 2 + 0.1 * theta.square().sum()


def run_cases():
    design = tensor([[1, 0], [1, 1], [1, 2]])
    y = tensor([0.5, 1.5, 2.2])
    theta = tensor([0.2, 0.7]).requires_grad_()

    def f(value):
        return audited_loss(value, design, y)

    hessian = torch.autograd.functional.hessian(f, theta)
    expected = design.T @ design + 0.2 * torch.eye(2, dtype=DTYPE)
    assert torch.allclose(hessian, expected, atol=1e-12, rtol=0)
    passed = torch.autograd.gradcheck(f, (theta,), eps=1e-6, atol=1e-5, rtol=1e-3)

    def detached(value):
        return ((design @ value).detach() - y).square().sum() / 2 + 0 * value.sum()

    bad = torch.autograd.gradcheck(detached, (theta,), raise_exception=False)
    assert passed and not bad
    inplace_rejected = False
    try:
        theta.add_(1)
    except RuntimeError:
        inplace_rejected = True
    assert inplace_rejected
    return {
        "hessian": hessian.tolist(),
        "minimum_information_eigenvalue": float(torch.linalg.eigvalsh(hessian)[0]),
        "correct_gradcheck": passed,
        "detached_gradcheck": bad,
        "leaf_inplace_operation_rejected": inplace_rejected,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
