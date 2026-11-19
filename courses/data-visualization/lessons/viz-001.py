"""viz-001: learner source. Read the guide and keep your own saved draft."""

import plotly.graph_objects as go

FIXTURE = [["u1", "Alpha", 2], ["u2", "Beta", 5], ["u3", "Gamma", 3]]


def build_figure():
    """Derive traces, axis titles and units from FIXTURE as the guide describes."""
    fig = go.Figure()
    # TODO 1: Trace identity.
    # TODO 2: Build the figure.
    # TODO 3: Change the measurement.
    # TODO 4: Diagnose a mismatch.
    # TODO 5: Handle empty input.
    # TODO 6: Transfer the encoding.
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
