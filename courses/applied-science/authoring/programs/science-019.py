"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def dl_meta(effect, variance):
    y, v = np.asarray(effect, float), np.asarray(variance, float)
    w = 1 / v
    fixed = float(w @ y / w.sum())
    q = float(w @ ((y - fixed) ** 2))
    c = float(w.sum() - (w @ w) / w.sum())
    tau2 = max(0.0, (q - (len(y) - 1)) / c)
    random_w = 1 / (v + tau2)
    mean = float(random_w @ y / random_w.sum())
    se = float(np.sqrt(1 / random_w.sum()))
    return dict(mean=mean, se=se, tau2=tau2, q=q, weights=random_w)


def run_cases():
    y = np.array([0.1, 0.2, 0.7, 0.9])
    v = np.array([0.04, 0.04, 0.04, 0.04])
    r = dl_meta(y, v)
    assert np.isclose(r["mean"], 0.475) and r["tau2"] > 0
    confidence = 1.96 * r["se"]
    prediction = 1.96 * np.sqrt(r["se"] ** 2 + r["tau2"])
    assert prediction > confidence
    equal = dl_meta([0.2, 0.2, 0.2], [0.04, 0.04, 0.04])
    assert equal["tau2"] == 0
    return dict(
        mean=r["mean"],
        tau2=r["tau2"],
        confidence_halfwidth=float(confidence),
        prediction_halfwidth=float(prediction),
    )


def render_figure(evidence):
    import plotly.graph_objects as go

    labels = ["Study1", "Study2", "Study3", "Study4"]
    values = [0.1, 0.2, 0.7, 0.9]
    fig = go.Figure(
        go.Scatter(
            x=values, y=labels, mode="markers", error_x=dict(type="constant", value=1.96 * 0.2)
        )
    )
    fig.add_vline(x=evidence["mean"], line_dash="dash")
    fig.update_layout(
        title="Observed effects and illustrative within-study intervals",
        xaxis_title="Additive effect",
        meta=dict(
            description="Four synthetic effects with common standard error 0.2; dashed line marks pooled mean 0.475. Intervals illustrate a normal approximation.",
            table=dict(
                columns=["Study", "Effect", "Standard error"],
                rows=[[label, value, 0.2] for label, value in zip(labels, values, strict=True)],
            ),
        ),
    )
    fig.show()


if __name__ == "__main__":
    evidence = run_cases()
    print("science-019 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
    render_figure(evidence)
