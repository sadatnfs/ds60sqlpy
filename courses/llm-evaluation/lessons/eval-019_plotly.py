import numpy as np


def probability_vector(values):
    x = np.asarray(values, float)
    if (
        x.ndim != 1
        or not x.size
        or not np.isfinite(x).all()
        or np.any(x <= 0)
        or not np.isclose(x.sum(), 1)
    ):
        raise ValueError("Strictly positive normalized probabilities required")
    return x


def softmax(logits):
    x = np.asarray(logits, float)
    weights = np.exp(x - x.max())
    return weights / weights.sum()


def objective(p, q, reward, beta):
    p = probability_vector(p)
    q = probability_vector(q)
    r = np.asarray(reward, float)
    if p.shape != q.shape or p.shape != r.shape or beta <= 0 or not np.isfinite(r).all():
        raise ValueError("Aligned rewards and positive beta required")
    return float(p @ r - beta * np.sum(p * np.log(p / q)))


def optimal_policy(q, reward, beta):
    q = probability_vector(q)
    r = np.asarray(reward, float)
    if r.shape != q.shape or beta <= 0 or not np.isfinite(r).all() or not np.isfinite(beta):
        raise ValueError("Invalid policy objective")
    return softmax(np.log(q) + r / beta)


def logit_gradient(logits, q, reward, beta):
    p = softmax(logits)
    direction = np.asarray(reward) - beta * (np.log(p / np.asarray(q)) + 1)
    return p * (direction - p @ direction)


def show_curve():
    import plotly.graph_objects as go

    rows = []
    for beta in [0.1, 0.2, 0.5, 1.0, 2.0, 5.0]:
        p = optimal_policy([0.5, 0.5], [1.0, 0.0], beta)
        divergence = float(np.sum(p * np.log(p / 0.5)))
        rows.append([beta, float(p[0]), divergence, objective(p, [0.5, 0.5], [1.0, 0.0], beta)])
    assert all(a[1] > b[1] for a, b in zip(rows, rows[1:], strict=False))
    figure = go.Figure(
        go.Scatter(
            x=[r[0] for r in rows],
            y=[r[1] for r in rows],
            mode="lines+markers",
            customdata=[[r[2]] for r in rows],
            hovertemplate=(
                "Beta=%{x}<br>Preferred-action "
                "probability=%{y}<br>KL=%{customdata[0]}<extra></extra>"
            ),
        )
    )
    figure.update_layout(
        title="Finite-policy regularization tradeoff",
        xaxis={"title": "Beta", "type": "log"},
        yaxis={"title": "Probability of action 0", "range": [0.5, 1]},
        meta={
            "description": (
                "For the stated two-action reward and uniform reference, "
                "increasing beta moves the exact optimum toward the "
                "reference. These are objective calculations, not observed "
                "language-model responses."
            ),
            "table": {
                "columns": ["Beta", "Action 0 probability", "KL to reference", "Objective"],
                "rows": rows,
            },
        },
    )
    figure.show()
    print("eval-019 Plotly curve complete")


if __name__ == "__main__":
    show_curve()
