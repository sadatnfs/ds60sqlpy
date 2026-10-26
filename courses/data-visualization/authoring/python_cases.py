"""Durable standalone Plotly teaching programs. Every case returns its figure."""

import hashlib
import json
import textwrap

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def describe(fig, title, description, columns, rows):
    fig.update_layout(
        title={
            "text": "<br>".join(textwrap.wrap(title, width=28)),
            "font": {"size": 16},
            "x": 0,
            "xanchor": "left",
            "automargin": True,
        },
        template="plotly_white",
        height=440,
        margin={"l": 65, "r": 25, "t": 90, "b": 65},
        meta={"description": description, "table": {"columns": columns, "rows": rows}},
    )
    assert len(columns) <= 12 and len(rows) <= 100
    print(title)
    print(description)
    print(" | ".join(columns))
    for row in rows:
        print(" | ".join(str(value) for value in row))
    assert len(fig.to_json().encode()) <= 200 * 1024
    return fig


def case_01():
    records = [("u1", "Alpha", 2.0), ("u2", "Beta", 5.0), ("u3", "Gamma", 3.0)]
    ordered = sorted(records, key=lambda row: row[2], reverse=True)
    fig = go.Figure(
        go.Bar(
            x=[row[1] for row in ordered],
            y=[row[2] for row in ordered],
            customdata=[[row[0]] for row in ordered],
            text=[row[2] for row in ordered],
            textposition="outside",
            marker_color="#176b87",
            hovertemplate="%{x}: %{y:.1f} hours (record %{customdata[0]})<extra></extra>",
        )
    )
    fig.update_xaxes(title="Team")
    fig.update_yaxes(title="Elapsed hours", rangemode="tozero")
    assert sum(row[2] for row in ordered) == 10 and ordered[0][0] == "u2"
    # A label/value shuffle would still draw bars but fail this identity check.
    assert dict(zip(fig.data[0].x, fig.data[0].y, strict=True)) == {
        "Beta": 5,
        "Gamma": 3,
        "Alpha": 2,
    }
    return describe(
        fig,
        "Three measured completion times",
        (
            "Beta takes five hours, Gamma three and Alpha two. These are three"
            " records, not uncertainty estimates."
        ),
        ["record", "team", "hours"],
        [list(row) for row in ordered],
    )


def case_02():
    raw = [1, 1, 2, 2, 3, 4, 6, 8, 10, 12, None]
    values = np.array([value for value in raw if value is not None], dtype=float)
    edges = np.array([0, 3, 6, 9, 13], dtype=float)
    counts, _ = np.histogram(values, bins=edges)
    widths = np.diff(edges)
    density = counts / (len(values) * widths)
    ordered, frequencies = np.unique(values, return_counts=True)
    probability = np.cumsum(frequencies) / len(values)
    fig = make_subplots(
        rows=1, cols=2, subplot_titles=["Density with unequal bins", "Empirical CDF"]
    )
    fig.add_trace(
        go.Bar(
            x=((edges[:-1] + edges[1:]) / 2).tolist(),
            y=density.tolist(),
            width=widths.tolist(),
            name="density",
            marker_color="#176b87",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=[0.0] + ordered.tolist(),
            y=[0.0] + probability.tolist(),
            mode="lines+markers",
            line_shape="hv",
            name="ECDF",
            marker_symbol="square",
        ),
        row=1,
        col=2,
    )
    fig.update_xaxes(title="Duration (minutes)")
    fig.update_yaxes(title="Probability per minute", row=1, col=1)
    fig.update_yaxes(title="Fraction at or below", range=[0, 1.05], row=1, col=2)
    assert counts.tolist() == [4, 2, 2, 2] and np.isclose(density @ widths, 1)
    assert probability[-1] == 1 and len(raw) - len(values) == 1
    rows = [
        [float(edges[i]), float(edges[i + 1]), int(counts[i]), float(density[i])] for i in range(4)
    ]
    return describe(
        fig,
        "Distribution of ten observed durations",
        (
            "One missing duration is excluded, not coded zero. Unequal-bin "
            "density integrates to one; the ECDF reaches one."
        ),
        ["lower", "upper", "count", "density"],
        rows,
    )


def case_03():
    labels = ["North", "Central", "South"]
    effect = np.array([-0.4, 0.2, 0.8])
    se = np.array([0.1, 0.3, 0.2])
    lower, upper = effect - 1.96 * se, effect + 1.96 * se
    fig = go.Figure(
        go.Scatter(
            x=effect.tolist(),
            y=labels,
            mode="markers",
            marker={"size": 11, "symbol": "diamond"},
            error_x={
                "type": "data",
                "array": (upper - effect).tolist(),
                "arrayminus": (effect - lower).tolist(),
                "symmetric": False,
            },
            customdata=np.column_stack([lower, upper]).tolist(),
            hovertemplate=(
                "%{y}: %{x:.3f} points; 95% CI [%{customdata[0]:.3f}, "
                "%{customdata[1]:.3f}]<extra></extra>"
            ),
        )
    )
    fig.add_vline(x=0, line_dash="dash", line_color="#555")
    fig.update_xaxes(title="Mean difference (points)", range=[-0.8, 1.4])
    fig.update_yaxes(title="Prespecified region")
    assert lower[2] > 0 and lower[1] < 0 < upper[1]
    assert np.allclose((upper - lower) / se, 3.92)
    return describe(
        fig,
        "Regional effect estimates with marginal intervals",
        (
            "Intervals are separate normal-approximation 95% confidence "
            "intervals, not simultaneous intervals or individual outcome "
            "ranges."
        ),
        ["region", "effect", "lower95", "upper95"],
        [
            [label, float(a), float(b), float(c)]
            for label, a, b, c in zip(labels, effect, lower, upper, strict=True)
        ],
    )


def case_04():
    records = [[f"u{i}", "A" if i < 4 else "B", i, 2 * i + (i % 3)] for i in range(8)]
    fig = go.Figure()
    for group, symbol in [("A", "circle"), ("B", "square")]:
        subset = [row for row in records if row[1] == group]
        fig.add_trace(
            go.Scatter(
                x=[row[2] for row in subset],
                y=[row[3] for row in subset],
                customdata=[[row[0], row[1]] for row in subset],
                mode="markers",
                marker={"size": 12, "symbol": symbol},
                name=group,
                hovertemplate=(
                    "%{customdata[0]} (%{customdata[1]}): baseline %{x}, outcome "
                    "%{y}<extra></extra>"
                ),
            )
        )
    fig.update_layout(
        updatemenus=[
            {
                "type": "dropdown",
                "buttons": [
                    {"label": "All", "method": "update", "args": [{"visible": [True, True]}]},
                    {"label": "A", "method": "update", "args": [{"visible": [True, False]}]},
                    {"label": "B", "method": "update", "args": [{"visible": [False, True]}]},
                ],
            }
        ],
        uirevision="viz-004-fixture-v1",
    )
    fig.update_xaxes(title="Pretreatment activity")
    fig.update_yaxes(title="Observed outcome")
    assert sum(len(trace.x) for trace in fig.data) == 8
    assert [row[0] for row in records if row[1] == "B"] == ["u4", "u5", "u6", "u7"]
    return describe(
        fig,
        "Inspect groups without changing the underlying dataset",
        (
            "The dropdown changes visible traces. The table always contains "
            "all eight source records; filtering is exploratory and does not "
            "redefine the population."
        ),
        ["user", "group", "baseline", "outcome"],
        records,
    )


def case_05():
    history_dates = [f"2026-01-{day:02d}" for day in range(1, 7)]
    future_dates = [f"2026-01-{day:02d}" for day in range(7, 10)]
    history = [10, 11, 12, 13, 14, 15]
    forecast, actual = np.array([16, 17, 18]), np.array([17, 16, 19])
    lower, upper = forecast - 2, forecast + 2
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=history_dates, y=history, mode="lines+markers", name="Available history")
    )
    fig.add_trace(
        go.Scatter(
            x=future_dates + future_dates[::-1],
            y=upper.tolist() + lower[::-1].tolist(),
            fill="toself",
            fillcolor="rgba(23,107,135,0.15)",
            line={"width": 0},
            name="Illustrative predictive band",
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=future_dates,
            y=forecast.tolist(),
            mode="lines+markers",
            name="Frozen forecast",
            line_dash="dash",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=future_dates,
            y=actual.tolist(),
            mode="markers",
            name="Later observed",
            marker_symbol="x",
        )
    )
    fig.update_xaxes(title="Event date", type="date")
    fig.update_yaxes(title="Daily demand (units)")
    rmse = float(np.sqrt(np.mean((forecast - actual) ** 2)))
    assert rmse == 1 and np.all(lower <= upper)
    assert min(future_dates) > max(history_dates)
    print("Forecast RMSE:", rmse)
    return describe(
        fig,
        "A forecast frozen before its outcomes arrived",
        (
            "History ends January 6. Later observations are evaluated against "
            "a frozen forecast. The plus/minus two band is illustrative and "
            "has no asserted coverage calibration."
        ),
        ["date", "forecast", "actual", "lower", "upper"],
        [
            [date, int(predicted), int(observed), int(low), int(high)]
            for date, predicted, observed, low, high in zip(
                future_dates, forecast, actual, lower, upper, strict=True
            )
        ],
    )


def case_06():
    actual = np.arange(1, 9, dtype=float)
    a = actual + np.array([0.2, -0.2, 0.5, -0.5, 0.1, -0.1, 1, -1])
    b = actual + np.array([0.4, -0.4, 0.6, -0.6, 0.2, -0.2, 1.5, -1.5])
    difference = (a - actual) ** 2 - (b - actual) ** 2
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=["Same observations, same scales", "Paired squared-loss difference"],
    )
    fig.add_trace(
        go.Scatter(
            x=actual.tolist(), y=a.tolist(), mode="markers", name="Model A", marker_symbol="circle"
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=actual.tolist(), y=b.tolist(), mode="markers", name="Model B", marker_symbol="square"
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=[0, 10], y=[0, 10], mode="lines", line_dash="dash", name="Identity"),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(x=[f"u{i}" for i in range(8)], y=difference.tolist(), name="A loss minus B loss"),
        row=1,
        col=2,
    )
    fig.update_xaxes(title="Observed", range=[0, 10], row=1, col=1)
    fig.update_yaxes(title="Predicted", range=[0, 10], row=1, col=1)
    fig.update_xaxes(title="Held-out user", row=1, col=2)
    fig.update_yaxes(title="Squared units", row=1, col=2)
    assert np.all(difference < 0) and np.isclose(difference.mean(), -0.3775)
    return describe(
        fig,
        "A paired model comparison",
        (
            "Both models use the same eight held-out users. Negative paired "
            "differences favor A; these eight values alone do not establish a "
            "population performance guarantee."
        ),
        ["user", "observed", "A", "B", "A_loss_minus_B"],
        [
            [f"u{i}", float(actual[i]), float(a[i]), float(b[i]), float(difference[i])]
            for i in range(8)
        ],
    )


def envelope_indices(values, block=100):
    keep = {0, len(values) - 1}
    for start in range(0, len(values), block):
        chunk = values[start : start + block]
        keep.add(start + int(np.argmin(chunk)))
        keep.add(start + int(np.argmax(chunk)))
    return np.array(sorted(keep))


def case_07():
    x = np.arange(5000)
    y = np.sin(x / 40)
    y[2473] = 12
    stride = np.arange(0, len(x), 100)
    keep = envelope_indices(y)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x[stride].tolist(),
            y=y[stride].tolist(),
            mode="lines+markers",
            name="Regular stride",
            line_dash="dot",
        )
    )
    fig.add_trace(
        go.Scatter(x=x[keep].tolist(), y=y[keep].tolist(), mode="lines", name="Min/max envelope")
    )
    fig.update_xaxes(title="Sample index")
    fig.update_yaxes(title="Measured amplitude")
    assert 2473 in keep and 2473 not in stride
    assert len(keep) <= 102 and y[keep].max() == y.max() == 12
    assert y[stride].max() < 1.1
    return describe(
        fig,
        "Reduce displayed points without silently losing the largest spike",
        (
            "The original has 5,000 samples. A min/max envelope preserves each"
            " block's extrema, while a regular stride misses sample 2473. "
            "Neither reduction preserves every shape, frequency or average."
        ),
        ["representation", "points", "maximum", "spike_retained"],
        [
            ["original", len(y), float(y.max()), True],
            ["stride", len(stride), float(y[stride].max()), False],
            ["envelope", len(keep), float(y[keep].max()), True],
        ],
    )


def case_08():
    counts = {"completed": 8, "pending": 3, "failed": 1}
    fig = go.Figure(
        go.Bar(
            x=list(counts),
            y=list(counts.values()),
            text=list(counts.values()),
            textposition="outside",
            marker_color=["#176b87", "#a66000", "#a61c3c"],
            marker_pattern_shape=["", "/", "x"],
        )
    )
    fig.update_xaxes(title="Recorded status")
    fig.update_yaxes(title="Jobs", rangemode="tozero")
    fig = describe(
        fig,
        "Twelve jobs at a declared observation cutoff",
        (
            "Eight completed, three pending and one failed. Pending is not "
            "failure. Labels, bar patterns and the table preserve meaning "
            "without relying only on color."
        ),
        ["status", "count"],
        [[key, value] for key, value in counts.items()],
    )
    spec = fig.to_json()
    restored = go.Figure(json.loads(spec))
    assert list(restored.data[0].y) == [8, 3, 1] and sum(restored.data[0].y) == 12
    assert restored.layout.meta["table"]["rows"] == fig.layout.meta["table"]["rows"]
    print(
        "Figure specification bytes:",
        len(spec.encode()),
        "SHA256:",
        hashlib.sha256(spec.encode()).hexdigest(),
    )
    return fig
