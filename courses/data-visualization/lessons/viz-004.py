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


def main():
    # Derive the chart and accessible table from FIXTURE.
    # Follow the six tasks in the guide; the worked reference is separate.
    print("Prepared Plotly figure type:", go.Figure.__name__)
    print("Fixture loaded; derive the figure and its checks from the guide tasks.")


if __name__ == "__main__":
    main()
