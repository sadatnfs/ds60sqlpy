import numpy as np


def identity_wins(left_wins, a_on_left):
    if len(left_wins) != len(a_on_left) or not left_wins:
        raise ValueError("Paired orientations required")
    if any(type(side) is not bool for side in a_on_left) or any(
        win not in (0, 0.5, 1) for win in left_wins
    ):
        raise ValueError("Known comparison labels and Boolean orientation required")
    return np.array(
        [float(win if left else 1 - win) for win, left in zip(left_wins, a_on_left, strict=True)]
    )


def calibration(probabilities, labels, edges=(0.0, 0.5, 1.0)):
    p = np.asarray(probabilities, float)
    y = np.asarray(labels, float)
    if (
        p.shape != y.shape
        or not p.size
        or np.any((p < 0) | (p > 1))
        or not np.isfinite(p).all()
        or np.any((y != 0) & (y != 1))
    ):
        raise ValueError("Invalid calibration records")
    edges = np.asarray(edges, float)
    if (
        edges.ndim != 1
        or len(edges) < 2
        or not np.isfinite(edges).all()
        or edges[0] != 0
        or edges[-1] != 1
        or np.any(np.diff(edges) <= 0)
    ):
        raise ValueError("Increasing probability bin edges required")
    bin_id = np.clip(np.searchsorted(edges, p, side="right") - 1, 0, len(edges) - 2)
    ece = 0.0
    for index in range(len(edges) - 1):
        take = bin_id == index
        if take.any():
            ece += take.mean() * abs(p[take].mean() - y[take].mean())
    return float(np.mean((p - y) ** 2)), float(ece)


def show_curve():
    import plotly.graph_objects as go

    p = np.array([0.9, 0.8, 0.2, 0.1])
    y = np.array([1, 1, 0, 0])
    rows = []
    for take in (p < 0.5, p >= 0.5):
        rows.append([float(p[take].mean()), float(y[take].mean()), int(take.sum())])
    assert [row[2] for row in rows] == [2, 2]
    figure = go.Figure()
    figure.add_scatter(x=[0, 1], y=[0, 1], mode="lines", name="Identity reference")
    figure.add_scatter(
        x=[r[0] for r in rows],
        y=[r[1] for r in rows],
        mode="markers",
        name="Authored bins",
        customdata=[[r[2]] for r in rows],
        hovertemplate=(
            "Mean score=%{x}<br>Observed rate=%{y}<br>Count=%{customdata[0]}<extra></extra>"
        ),
    )
    figure.update_layout(
        title="Reliability table with two observations per bin",
        xaxis_title="Mean stated probability",
        yaxis_title="Observed fraction correct",
        xaxis_range=[0, 1],
        yaxis_range=[0, 1],
        meta={
            "description": (
                "Two synthetic observations contribute to each bin. The plot "
                "is descriptive; it supplies no precise population "
                "calibration claim or uncertainty band."
            ),
            "table": {"columns": ["Mean probability", "Observed rate", "Count"], "rows": rows},
        },
    )
    figure.show()
    print("eval-011 Plotly curve complete")


if __name__ == "__main__":
    show_curve()
