"""viz-007: learner source. Read the guide and keep your own saved draft."""

import plotly.graph_objects as go

FIXTURE = {"count": 5000, "spike_index": 2473, "spike_value": 12, "block": 100}


def main():
    # Derive the chart and accessible table from FIXTURE.
    # Follow the six tasks in the guide; the worked reference is separate.
    print("Prepared Plotly figure type:", go.Figure.__name__)
    print("Fixture loaded; derive the figure and its checks from the guide tasks.")


if __name__ == "__main__":
    main()
