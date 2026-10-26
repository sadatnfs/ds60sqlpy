"""viz-006: complete offline Plotly reference."""

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


def main():
    figure = case_06()
    figure.show(config={"responsive": True, "displaylogo": False})
    print("viz-006 Plotly complete")


if __name__ == "__main__":
    main()
