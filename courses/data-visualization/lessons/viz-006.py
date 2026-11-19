"""viz-006: learner source. Read the guide and keep your own saved draft."""

import plotly.graph_objects as go

FIXTURE = [[1, 0.2], [2, -0.2], [3, 0.5], [4, -0.5], [5, 0.1], [6, -0.1], [7, 1], [8, -1]]


def build_figure():
    """Derive traces, axis titles and units from FIXTURE as the guide describes."""
    fig = go.Figure()
    # TODO 1: Calculate one paired loss.
    # TODO 2: Build two panels.
    # TODO 3: Change one failure.
    # TODO 4: Repair a misleading comparison.
    # TODO 5: Aggregate by meaningful groups.
    # TODO 6: Transfer to repeated visits.
    # Add traces with fig.add_trace(go.Bar(...)) or fig.add_trace(go.Scatter(...)).
    fig.update_layout(title="Describe the measured quantity and its units")
    return fig


def main():
    figure = build_figure()
    print("Fixture records:", FIXTURE)
    print("Traces so far:", len(figure.data))
    # When the figure and its table are complete, display it with figure.show().


if __name__ == "__main__":
    main()
