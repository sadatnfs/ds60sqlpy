// viz-004: learner source for the prepared browser Plotly variant.
// window.Plotly, #chart and #output are supplied. No imports or fetches.
const fixture = [
  ["u0", "A", 0, 0],
  ["u1", "A", 1, 3],
  ["u2", "A", 2, 6],
  ["u3", "A", 3, 6],
  ["u4", "B", 4, 9],
  ["u5", "B", 5, 12],
  ["u6", "B", 6, 12],
  ["u7", "B", 7, 15],
];
console.table(fixture);
// Derive your traces, caption and native source table from fixture.
// TODO 1: Trace groups.
// TODO 2: Implement filters.
// TODO 3: Preserve hover identity.
// TODO 4: Debug selection clearing.
// TODO 5: Review keyboard and table access.
// TODO 6: Transfer to missing groups.
const traces = [];
const layout = { title: { text: "Describe the measured quantity and its units" } };
if (typeof Plotly !== "undefined" && traces.length > 0) {
  Plotly.newPlot(document.getElementById("chart"), traces, layout);
}
console.log("Fixture loaded; derive the figure and its checks from the guide tasks.");
