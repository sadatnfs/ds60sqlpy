"""viz-008: learner source. Read the guide and keep your own saved draft."""

import plotly.graph_objects as go

FIXTURE = {"completed": 8, "pending": 3, "failed": 1}


def build_figure():
    """Derive traces, axis titles and units from FIXTURE as the guide describes."""
    fig = go.Figure()
    # TODO 1: Audit the denominator.
    # TODO 2: Add redundant encodings.
    # TODO 3: Round-trip JSON.
    # TODO 4: Detect an edited claim.
    # TODO 5: Review a narrow view.
    # TODO 6: Transfer to a scientific report.
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
