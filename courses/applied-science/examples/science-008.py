"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np
from scipy import optimize


def reconcile(base, summing, covariance):
    s = np.asarray(summing, float)
    w = np.asarray(covariance, float)
    precision = np.linalg.solve(w, np.eye(len(w)))
    bottom = np.linalg.solve(s.T @ precision @ s, s.T @ precision @ np.asarray(base))
    return s @ bottom


def run_cases():
    s = np.array([[1.0, 1.0], [1.0, 0.0], [0.0, 1.0]])
    base = np.array([12.0, 4.0, 5.0])
    rec = reconcile(base, s, np.eye(3))
    assert np.allclose(rec, [11.0, 5.0, 6.0]) and rec[0] == rec[1] + rec[2]
    coherent = np.array([9.0, 4.0, 5.0])
    assert np.allclose(reconcile(coherent, s, np.eye(3)), coherent)
    certain_total = reconcile(base, s, np.diag([0.01, 4, 4]))
    assert abs(certain_total[0] - 12) < abs(rec[0] - 12)
    # Coherence alone can be compatible with an implausible negative component.
    unrestricted = reconcile([1.0, -8.0, 4.0], s, np.eye(3))
    constrained = optimize.lsq_linear(s, np.array([1.0, -8.0, 4.0]), bounds=(0, np.inf)).x
    assert unrestricted[1] < 0 and np.all(constrained >= 0)
    return dict(
        ols=rec.tolist(), weighted=certain_total.tolist(), nonnegative_bottom=constrained.tolist()
    )


def render_figure(evidence):
    import plotly.graph_objects as go

    labels = ["Total", "First component", "Second component"]
    base = [12, 4, 5]
    adjusted = evidence["ols"]
    fig = go.Figure(
        [
            go.Bar(name="Base forecast", x=labels, y=base),
            go.Bar(name="Coherent forecast", x=labels, y=adjusted),
        ]
    )
    fig.update_layout(
        title="Forecast coherence under identity covariance",
        barmode="group",
        meta=dict(
            description="Base total 12 differs from components 4+5; reconciliation yields 11=5+6.",
            table=dict(
                columns=["Series", "Base", "Coherent"],
                rows=[list(row) for row in zip(labels, base, adjusted, strict=True)],
            ),
        ),
    )
    fig.show()


if __name__ == "__main__":
    evidence = run_cases()
    print("science-008 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
    render_figure(evidence)
