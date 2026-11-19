// viz-007: learner source for the prepared browser Plotly variant.
// window.Plotly, #chart and #output are supplied. No imports or fetches.
const fixture = { count: 5000, spike_index: 2473, spike_value: 12, block: 100 };
console.table(fixture);
// Derive your traces, caption and native source table from fixture.
// TODO 1: Find the missed spike.
// TODO 2: Implement an envelope.
// TODO 3: Change the block size.
// TODO 4: Expose a limitation.
// TODO 5: Test lifecycle behavior.
// TODO 6: Transfer the objective.
const traces = [];
const layout = { title: { text: "Describe the measured quantity and its units" } };
if (typeof Plotly !== "undefined" && traces.length > 0) {
  Plotly.newPlot(document.getElementById("chart"), traces, layout);
}
console.log("Fixture loaded; derive the figure and its checks from the guide tasks.");
