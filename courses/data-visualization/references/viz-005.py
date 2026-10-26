"""viz-005: complete offline Plotly reference."""

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


def main():
    figure = case_05()
    figure.show(config={"responsive": True, "displaylogo": False})
    print("viz-005 Plotly complete")


if __name__ == "__main__":
    main()
