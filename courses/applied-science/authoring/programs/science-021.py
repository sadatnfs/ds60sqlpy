"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json
from itertools import combinations

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
    # Six locations and three ones allow only C(6, 3) = 20 arrangements: enumerate them all.
    reference = []
    for ones in combinations(range(6), 3):
        values = np.zeros(6)
        values[list(ones)] = 1
        reference.append(moran(values, w))
    p = float(np.mean(np.array(reference) >= clustered - 1e-12))
    assert len(reference) == 20 and np.isclose(p, 0.1)  # 2 of 20 arrangements
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
        reference_arrangements=len(reference),
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
