// viz-006: learner source for the prepared browser Plotly variant.
// window.Plotly, #chart and #output are supplied. No imports or fetches.
const fixture = [
  [1, 0.2],
  [2, -0.2],
  [3, 0.5],
  [4, -0.5],
  [5, 0.1],
  [6, -0.1],
  [7, 1],
  [8, -1],
];
console.table(fixture);
// Derive your traces, caption and native source table from fixture.
// TODO 1: Calculate one paired loss.
// TODO 2: Build two panels.
// TODO 3: Change one failure.
// TODO 4: Repair a misleading comparison.
// TODO 5: Aggregate by meaningful groups.
// TODO 6: Transfer to repeated visits.
const traces = [];
const layout = { title: { text: "Describe the measured quantity and its units" } };
if (typeof Plotly !== "undefined" && traces.length > 0) {
  Plotly.newPlot(document.getElementById("chart"), traces, layout);
}
console.log("Fixture loaded; derive the figure and its checks from the guide tasks.");
