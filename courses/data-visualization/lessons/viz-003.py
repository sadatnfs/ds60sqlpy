"""viz-003: learner source. Read the guide and keep your own saved draft."""

import plotly.graph_objects as go

FIXTURE = [["North", -0.4, 0.1], ["Central", 0.2, 0.3], ["South", 0.8, 0.2]]


def main():
    # Derive the chart and accessible table from FIXTURE.
    # Follow the six tasks in the guide; the worked reference is separate.
    print("Prepared Plotly figure type:", go.Figure.__name__)
    print("Fixture loaded; derive the figure and its checks from the guide tasks.")


if __name__ == "__main__":
    main()
