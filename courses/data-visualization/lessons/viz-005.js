// viz-005: learner source for the prepared browser Plotly variant.
// window.Plotly, #chart and #output are supplied. No imports or fetches.
const fixture = [
  ["2026-01-07", 16, 17],
  ["2026-01-08", 17, 16],
  ["2026-01-09", 18, 19],
];
console.table(fixture);
// Derive your traces, caption and native source table from fixture.
// TODO 1: Trace chronology.
// TODO 2: Compute errors.
// TODO 3: Construct the band.
// TODO 4: Diagnose a gap.
// TODO 5: Distinguish interval types.
// TODO 6: Transfer to delayed labels.
const traces = [];
const layout = { title: { text: "Describe the measured quantity and its units" } };
if (typeof Plotly !== "undefined" && traces.length > 0) {
  Plotly.newPlot(document.getElementById("chart"), traces, layout);
}
console.log("Fixture loaded; derive the figure and its checks from the guide tasks.");
