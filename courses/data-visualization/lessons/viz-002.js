// viz-002: learner source for the prepared browser Plotly variant.
// window.Plotly, #chart and #output are supplied. No imports or fetches.
const fixture = [1, 1, 2, 2, 3, 4, 6, 8, 10, 12, null];
console.table(fixture);
// Derive your traces, caption and native source table from fixture.
// TODO 1: Trace boundaries.
// TODO 2: Compute density.
// TODO 3: Change bins.
// TODO 4: Expose a bad missing-value policy.
// TODO 5: Render the tied ECDF.
// TODO 6: Transfer to rates.
const traces = [];
const layout = { title: { text: "Describe the measured quantity and its units" } };
if (typeof Plotly !== "undefined" && traces.length > 0) {
  Plotly.newPlot(document.getElementById("chart"), traces, layout);
}
console.log("Fixture loaded; derive the figure and its checks from the guide tasks.");
