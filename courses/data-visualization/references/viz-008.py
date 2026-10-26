"""viz-008: complete offline Plotly reference."""

import hashlib
import json
import textwrap

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


def main():
    figure = case_08()
    figure.show(config={"responsive": True, "displaylogo": False})
    print("viz-008 Plotly complete")


if __name__ == "__main__":
    main()
