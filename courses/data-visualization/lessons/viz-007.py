"""viz-007: learner source. Read the guide and keep your own saved draft."""

import plotly.graph_objects as go

FIXTURE = {"count": 5000, "spike_index": 2473, "spike_value": 12, "block": 100}


def build_figure():
    """Derive traces, axis titles and units from FIXTURE as the guide describes."""
    fig = go.Figure()
    # TODO 1: Find the missed spike.
    # TODO 2: Implement an envelope.
    # TODO 3: Change the block size.
    # TODO 4: Expose a limitation.
    # TODO 5: Test lifecycle behavior.
    # TODO 6: Transfer the objective.
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
