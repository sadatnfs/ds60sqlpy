// viz-001: learner source for the prepared browser Plotly variant.
// window.Plotly, #chart and #output are supplied. No imports or fetches.
const fixture = [
  ["u1", "Alpha", 2],
  ["u2", "Beta", 5],
  ["u3", "Gamma", 3],
];
console.table(fixture);
// Derive your traces, caption and native source table from fixture.
// TODO 1: Trace identity.
// TODO 2: Build the figure.
// TODO 3: Change the measurement.
// TODO 4: Diagnose a mismatch.
// TODO 5: Handle empty input.
// TODO 6: Transfer the encoding.
const traces = [];
const layout = { title: { text: "Describe the measured quantity and its units" } };
if (typeof Plotly !== "undefined" && traces.length > 0) {
  Plotly.newPlot(document.getElementById("chart"), traces, layout);
}
console.log("Fixture loaded; derive the figure and its checks from the guide tasks.");
