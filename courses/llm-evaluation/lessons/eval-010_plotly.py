import numpy as np


def policy_metrics(scores, correct, threshold, wrong_cost=5.0, abstain_cost=0.4):
    p = np.asarray(scores, float)
    y = np.asarray(correct, float)
    if (
        p.shape != y.shape
        or not p.size
        or not np.isfinite(p).all()
        or np.any((p < 0) | (p > 1))
        or np.any((y != 0) & (y != 1))
        or not 0 <= threshold <= 1
    ):
        raise ValueError("Invalid selective evaluation")
    if not np.isfinite([wrong_cost, abstain_cost]).all() or wrong_cost < 0 or abstain_cost < 0:
        raise ValueError("Finite nonnegative costs required")
    answered = p >= threshold
    return {
        "coverage": float(answered.mean()),
        "accuracy": float(y[answered].mean()) if answered.any() else None,
        "cost": float(np.mean(np.where(answered, wrong_cost * (1 - y), abstain_cost))),
    }


def choose_threshold(scores, correct, thresholds):
    return min(thresholds, key=lambda t: (policy_metrics(scores, correct, t)["cost"], t))


def show_curve():
    import plotly.graph_objects as go

    thresholds = [0.0, 0.25, 0.5, 0.75, 0.85, 0.95]
    rows = []
    for threshold in thresholds:
        result = policy_metrics([0.9, 0.8, 0.4, 0.2], [1, 0, 1, 0], threshold)
        risk = None if result["accuracy"] is None else 1 - result["accuracy"]
        rows.append([threshold, result["coverage"], risk, result["cost"]])
    assert rows[0][1:3] == [1.0, 0.5] and rows[-1][1:3] == [0.0, None]
    figure = go.Figure(
        go.Scatter(
            x=[r[1] for r in rows],
            y=[r[2] for r in rows],
            mode="lines+markers",
            customdata=[[r[0], r[3]] for r in rows],
            hovertemplate="Coverage=%{x}<br>Risk=%{y}<br>Threshold=%{customdata[0]}<br>Cost=%{customdata[1]}<extra></extra>",
        )
    )
    figure.update_layout(
        title="Authored selective-risk curve",
        xaxis_title="Fraction answered",
        yaxis_title="Wrong fraction among answers",
        xaxis_range=[0, 1],
        yaxis_range=[0, 1],
        meta={
            "description": (
                "The authored score ordering has a nonmonotone risk-coverage "
                "curve. At zero coverage risk is undefined. Threshold 0.85 "
                "answers one of four requests correctly; this is not a "
                "population guarantee."
            ),
            "table": {"columns": ["Threshold", "Coverage", "Selective risk", "Cost"], "rows": rows},
        },
    )
    figure.show()
    print("eval-010 Plotly curve complete")


if __name__ == "__main__":
    show_curve()
