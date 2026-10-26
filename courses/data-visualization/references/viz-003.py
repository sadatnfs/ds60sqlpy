"""viz-003: complete offline Plotly reference."""

import textwrap

import numpy as np
import plotly.graph_objects as go


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


def main():
    figure = case_03()
    figure.show(config={"responsive": True, "displaylogo": False})
    print("viz-003 Plotly complete")


if __name__ == "__main__":
    main()
