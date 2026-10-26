"""viz-007: complete offline Plotly reference."""

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


def main():
    figure = case_07()
    figure.show(config={"responsive": True, "displaylogo": False})
    print("viz-007 Plotly complete")


if __name__ == "__main__":
    main()
