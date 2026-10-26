"""viz-004: complete offline Plotly reference."""

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


def main():
    figure = case_04()
    figure.show(config={"responsive": True, "displaylogo": False})
    print("viz-004 Plotly complete")


if __name__ == "__main__":
    main()
