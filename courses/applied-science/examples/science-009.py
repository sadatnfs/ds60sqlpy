"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def pinball(y, q, tau):
    residual = np.asarray(y) - q
    return np.maximum(tau * residual, (tau - 1) * residual)


def run_cases():
    demand = np.array([0.0, 1.0, 1.0, 2.0, 3.0, 8.0])
    under, over = 4.0, 1.0
    tau = under / (under + over)
    candidates = np.arange(9.0)
    loss = np.array(
        [
            np.mean(under * np.maximum(demand - q, 0) + over * np.maximum(q - demand, 0))
            for q in candidates
        ]
    )
    optimum = float(candidates[np.argmin(loss)])
    assert optimum == 3 and np.allclose(
        loss, (under + over) * np.array([pinball(demand, q, tau).mean() for q in candidates])
    )
    # Mean-accurate models need not minimize asymmetric inventory cost.
    mean_quantity = float(demand.mean())
    mean_cost = float(
        np.mean(
            under * np.maximum(demand - mean_quantity, 0)
            + over * np.maximum(mean_quantity - demand, 0)
        )
    )
    assert mean_cost > loss.min()
    # Calibration by horizon, not an aggregate whose errors can cancel.
    covered = np.array([[1, 1, 1, 1, 1], [0, 0, 1, 0, 1]], bool)
    return dict(
        critical_fractile=tau,
        optimal_quantity=optimum,
        minimum_cost=float(loss.min()),
        mean_policy_cost=mean_cost,
        coverage_by_horizon=covered.mean(axis=1).tolist(),
    )


def render_figure(evidence):
    import plotly.graph_objects as go

    demand = np.array([0.0, 1.0, 1.0, 2.0, 3.0, 8.0])
    quantities = list(range(9))
    costs = [float(5 * pinball(demand, q, 0.8).mean()) for q in quantities]
    fig = go.Figure(go.Scatter(x=quantities, y=costs, mode="lines+markers"))
    fig.update_layout(
        title="Asymmetric inventory cost by quantity",
        xaxis_title="Quantity",
        yaxis_title="Mean cost",
        meta=dict(
            description="Underage costs four and overage one. The empirical decision cost is minimized at quantity three.",
            table=dict(
                columns=["Quantity", "Mean cost"],
                rows=[[q, c] for q, c in zip(quantities, costs, strict=True)],
            ),
        ),
    )
    fig.show()


if __name__ == "__main__":
    evidence = run_cases()
    print("science-009 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
    render_figure(evidence)
