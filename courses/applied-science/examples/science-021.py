"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def moran(values, weights):
    z = np.asarray(values, float)
    z = z - z.mean()
    w = np.asarray(weights, float)
    if np.isclose(z @ z, 0):
        raise ValueError("A constant map has no standardized spatial statistic")
    return float(len(z) / w.sum() * (z @ w @ z) / (z @ z))


def run_cases():
    w = np.zeros((6, 6))
    for i in range(5):
        w[i, i + 1] = w[i + 1, i] = 1
    clustered = moran([0, 0, 0, 1, 1, 1], w)
    alternating = moran([0, 1, 0, 1, 0, 1], w)
    assert clustered > 0 and alternating < 0
    rng = np.random.default_rng(21)
    permuted = [moran(rng.permutation([0, 0, 0, 1, 1, 1]), w) for _ in range(199)]
    p = (1 + sum(v >= clustered for v in permuted)) / 200
    assert 0 < p <= 1
    # Random row folds put neighboring locations in both sets; block folds do not.
    random_train = {0, 2, 4}
    block_train = {0, 1, 2}
    crossings = lambda train: sum(
        (i in train) != (j in train) for i in range(6) for j in range(i + 1, 6) if w[i, j]
    )
    assert crossings(random_train) > crossings(block_train)
    return dict(
        clustered_I=clustered,
        alternating_I=alternating,
        permutation_p=p,
        random_boundary_edges=crossings(random_train),
        blocked_boundary_edges=crossings(block_train),
    )


def render_figure(evidence):
    import plotly.graph_objects as go

    positions = list(range(6))
    values = [0, 0, 0, 1, 1, 1]
    fig = go.Figure(go.Scatter(x=positions, y=values, mode="lines+markers"))
    fig.update_layout(
        title="Values on an adjacency chain",
        xaxis_title="Graph position, not geographic distance",
        yaxis_title="Synthetic value",
        meta=dict(
            description="Three zeros followed by three ones on a six-node chain. Moran I is positive under nearest-neighbor adjacency.",
            table=dict(
                columns=["Graph position", "Value"],
                rows=[[a, b] for a, b in zip(positions, values, strict=True)],
            ),
        ),
    )
    fig.show()


if __name__ == "__main__":
    evidence = run_cases()
    print("science-021 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
    render_figure(evidence)
