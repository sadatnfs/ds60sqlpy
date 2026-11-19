// viz-003: learner source for the prepared browser Plotly variant.
// window.Plotly, #chart and #output are supplied. No imports or fetches.
const fixture = [
  ["North", -0.4, 0.1],
  ["Central", 0.2, 0.3],
  ["South", 0.8, 0.2],
];
console.table(fixture);
// Derive your traces, caption and native source table from fixture.
// TODO 1: Calculate bounds.
// TODO 2: Build error distances.
// TODO 3: Add a practical margin.
// TODO 4: Debug an asymmetric interval.
// TODO 5: Change the uncertainty target.
// TODO 6: Transfer to a family.
const traces = [];
const layout = { title: { text: "Describe the measured quantity and its units" } };
if (typeof Plotly !== "undefined" && traces.length > 0) {
  Plotly.newPlot(document.getElementById("chart"), traces, layout);
}
console.log("Fixture loaded; derive the figure and its checks from the guide tasks.");
