"""viz-001: complete offline Plotly reference."""

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


def main():
    figure = case_01()
    figure.show(config={"responsive": True, "displaylogo": False})
    print("viz-001 Plotly complete")


if __name__ == "__main__":
    main()
