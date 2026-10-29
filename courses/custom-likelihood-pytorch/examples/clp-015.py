"""Complete float64 CPU likelihood investigation with original synthetic data."""

from __future__ import annotations

import json

import torch

DTYPE = torch.float64
torch.set_num_threads(1)


def tensor(values):
    return torch.as_tensor(values, dtype=DTYPE)


def objective(raw, y):
    mean = torch.nn.functional.softplus(raw).square()
    return ((y - mean).square() / (2 * 0.5**2)).sum()


def fit(method, initial):
    y = tensor([1.4, 1.5, 1.6])
    raw = tensor(initial).requires_grad_()
    calls = 0
    if method == "lbfgs":
        optimizer = torch.optim.LBFGS(
            [raw],
            max_iter=80,
            tolerance_grad=1e-10,
            tolerance_change=1e-14,
            line_search_fn="strong_wolfe",
        )

        def closure():
            nonlocal calls
            calls += 1
            optimizer.zero_grad()
            loss = objective(raw, y)
            loss.backward()
            return loss

        returned = float(optimizer.step(closure).detach())
        steps = 1
    elif method == "adam":
        optimizer = torch.optim.Adam([raw], lr=0.06)
        steps = 600
        for _ in range(steps):
            optimizer.zero_grad()
            loss = objective(raw, y)
            loss.backward()
            optimizer.step()
            calls += 1
        returned = float(loss.detach())
    else:
        raise ValueError("Choose lbfgs or adam")
    final = objective(raw, y)
    gradient = torch.autograd.grad(final, raw)[0]
    return {
        "mean": float(torch.nn.functional.softplus(raw.detach()).square()),
        "final_objective": float(final.detach()),
        "gradient_abs": abs(float(gradient)),
        "optimizer_steps": steps,
        "objective_evaluations": calls,
        "returned_step_loss": returned,
    }


def run_cases():
    cases = {
        "lbfgs_low": fit("lbfgs", -1.5),
        "lbfgs_high": fit("lbfgs", 1.4),
        "adam_low": fit("adam", -1.5),
    }
    for value in cases.values():
        assert abs(value["mean"] - 1.5) < 2e-5 and value["gradient_abs"] < 3e-4
    assert cases["lbfgs_low"]["objective_evaluations"] > cases["lbfgs_low"]["optimizer_steps"]
    assert cases["lbfgs_low"]["returned_step_loss"] > cases["lbfgs_low"]["final_objective"]
    return {"cases": cases, "closed_form_target_mean": 1.5, "objective_has_fixed_known_scale": True}


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
