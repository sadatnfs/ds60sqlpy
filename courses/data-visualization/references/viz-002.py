"""viz-002: complete offline Plotly reference."""

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


def main():
    figure = case_02()
    figure.show(config={"responsive": True, "displaylogo": False})
    print("viz-002 Plotly complete")


if __name__ == "__main__":
    main()
