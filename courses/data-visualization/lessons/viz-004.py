"""viz-004: learner source. Read the guide and keep your own saved draft."""

import plotly.graph_objects as go

FIXTURE = [
    ["u0", "A", 0, 0],
    ["u1", "A", 1, 3],
    ["u2", "A", 2, 6],
    ["u3", "A", 3, 6],
    ["u4", "B", 4, 9],
    ["u5", "B", 5, 12],
    ["u6", "B", 6, 12],
    ["u7", "B", 7, 15],
]


def build_figure():
    """Derive traces, axis titles and units from FIXTURE as the guide describes."""
    fig = go.Figure()
    # TODO 1: Trace groups.
    # TODO 2: Implement filters.
    # TODO 3: Preserve hover identity.
    # TODO 4: Debug selection clearing.
    # TODO 5: Review keyboard and table access.
    # TODO 6: Transfer to missing groups.
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
