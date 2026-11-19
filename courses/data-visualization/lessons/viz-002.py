"""viz-002: learner source. Read the guide and keep your own saved draft."""

import plotly.graph_objects as go

FIXTURE = [1, 1, 2, 2, 3, 4, 6, 8, 10, 12, None]


def build_figure():
    """Derive traces, axis titles and units from FIXTURE as the guide describes."""
    fig = go.Figure()
    # TODO 1: Trace boundaries.
    # TODO 2: Compute density.
    # TODO 3: Change bins.
    # TODO 4: Expose a bad missing-value policy.
    # TODO 5: Render the tied ECDF.
    # TODO 6: Transfer to rates.
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
