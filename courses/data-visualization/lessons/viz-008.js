// viz-008: learner source for the prepared browser Plotly variant.
// window.Plotly, #chart and #output are supplied. No imports or fetches.
const fixture = { completed: 8, pending: 3, failed: 1 };
console.table(fixture);
// Derive your traces, caption and native source table from fixture.
// TODO 1: Audit the denominator.
// TODO 2: Add redundant encodings.
// TODO 3: Round-trip JSON.
// TODO 4: Detect an edited claim.
// TODO 5: Review a narrow view.
// TODO 6: Transfer to a scientific report.
const traces = [];
const layout = { title: { text: "Describe the measured quantity and its units" } };
if (typeof Plotly !== "undefined" && traces.length > 0) {
  Plotly.newPlot(document.getElementById("chart"), traces, layout);
}
console.log("Fixture loaded; derive the figure and its checks from the guide tasks.");
