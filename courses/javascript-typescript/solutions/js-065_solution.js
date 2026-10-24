// js-065: complete offline D3 browser reference.
if (typeof d3 !== "object" || d3.version !== "7.9.0")
  throw new Error("Prepared D3 7.9.0 is required.");
const host = document.querySelector("#chart");
const output = document.querySelector("#output");
if (!host || !output) throw new Error("Preview chart/output nodes are required.");
host.replaceChildren();
const check = (condition, message) => {
  if (!condition) throw new Error(message);
};
const svg = d3
  .select(host)
  .append("svg")
  .attr("viewBox", "0 0 640 360")
  .attr("role", "img")
  .attr("aria-label", "Dashboard state, cross-filtering and reproducible views")
  .style("width", "100%")
  .style("max-width", "640px");
svg.append("title").text("Dashboard state, cross-filtering and reproducible views");
const rows = Object.freeze(
  [
    { id: "A1", group: "A", value: 2 },
    { id: "A2", group: "A", value: 3 },
    { id: "B1", group: "B", value: 4 },
  ].map(Object.freeze),
);
let state = { group: "all" };
const summary = d3.select(host).append("p").attr("role", "status");
const controls = d3.select(host).append("div");
function render() {
  const visible = rows.filter((d) => state.group === "all" || d.group === state.group);
  svg
    .selectAll("rect")
    .data(visible, (d) => d.id)
    .join("rect")
    .attr("x", 100)
    .attr("y", (d, i) => 40 + i * 75)
    .attr("width", (d) => d.value * 90)
    .attr("height", 45)
    .attr("fill", "#7c3aed");
  summary.text(
    `${state.group}: ${visible.length} records; total ${d3.sum(visible, (d) => d.value)}`,
  );
  return visible;
}
const buttons = controls
  .selectAll("button")
  .data(["all", "A", "B"])
  .join("button")
  .attr("type", "button")
  .text((d) => `Show ${d}`)
  .on("click", (event, group) => {
    state = { group };
    render();
  });
render();
buttons.nodes()[1].click();
check(summary.text() === "A: 2 records; total 5", "Linked summary wrong");
check(svg.selectAll("rect").size() === 2, "Linked marks wrong");
buttons.nodes()[0].click();
check(render().length === 3 && rows[0].value === 2, "Reset or source preservation failed");

output.textContent = "js-065 D3 complete";
console.log("js-065 D3 complete");
