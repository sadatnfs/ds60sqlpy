// js-054: complete offline D3 browser reference.
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
  .attr("aria-label", "Reusable and responsive chart components")
  .style("width", "100%")
  .style("max-width", "640px");
svg.append("title").text("Reusable and responsive chart components");
const layer = svg.append("g");
function render(rows, width) {
  check(width > 0, "Width must be positive");
  const x = d3.scaleLinear().domain([0, 10]).range([0, width]);
  layer
    .selectAll("rect")
    .data(rows, (d) => d.id)
    .join("rect")
    .attr("x", 80)
    .attr("y", (d, i) => 50 + i * 70)
    .attr("width", (d) => x(d.value))
    .attr("height", 40)
    .attr("fill", "#0891b2");
  layer
    .selectAll("text.empty")
    .data(rows.length ? [] : [null])
    .join("text")
    .attr("class", "empty")
    .attr("x", 80)
    .attr("y", 100)
    .text("No observations");
}
render(
  [
    { id: "A", value: 3 },
    { id: "B", value: 6 },
  ],
  450,
);
render([{ id: "B", value: 6 }], 300);
check(layer.selectAll("rect").size() === 1, "Duplicate marks after update");
check(+layer.select("rect").attr("width") === 180, "Resize mapping wrong");
render([], 300);
check(
  layer.selectAll("rect").size() === 0 && layer.select(".empty").text() === "No observations",
  "Empty state failed",
);
render(
  [
    { id: "A", value: 3 },
    { id: "B", value: 6 },
  ],
  450,
);

output.textContent = "js-054 D3 complete";
console.log("js-054 D3 complete");
