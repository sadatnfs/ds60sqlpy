"""viz-003: learner source. Read the guide and keep your own saved draft."""

import plotly.graph_objects as go

FIXTURE = [["North", -0.4, 0.1], ["Central", 0.2, 0.3], ["South", 0.8, 0.2]]


def build_figure():
    """Derive traces, axis titles and units from FIXTURE as the guide describes."""
    fig = go.Figure()
    # TODO 1: Calculate bounds.
    # TODO 2: Build error distances.
    # TODO 3: Add a practical margin.
    # TODO 4: Debug an asymmetric interval.
    # TODO 5: Change the uncertainty target.
    # TODO 6: Transfer to a family.
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
