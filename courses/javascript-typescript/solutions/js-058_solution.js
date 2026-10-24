// js-058: complete offline D3 browser reference.
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
  .attr("aria-label", "Zoom, pan and rescaled axes")
  .style("width", "100%")
  .style("max-width", "640px");
svg.append("title").text("Zoom, pan and rescaled axes");
const rows = d3.range(11).map((x) => ({ x, y: Math.sin(x) }));
const base = d3.scaleLinear().domain([0, 10]).range([60, 590]);
const y = d3.scaleLinear().domain([-1, 1]).range([270, 40]);
const axis = svg.append("g").attr("transform", "translate(0,300)");
const marks = svg
  .selectAll("circle")
  .data(rows)
  .join("circle")
  .attr("cy", (d) => y(d.y))
  .attr("r", 5)
  .attr("fill", "#0f766e");
let view = base;
const zoom = d3
  .zoom()
  .extent([
    [60, 30],
    [590, 300],
  ])
  .scaleExtent([1, 4])
  .on("zoom", (event) => {
    view = event.transform.rescaleX(base);
    marks.attr("cx", (d) => view(d.x));
    axis.call(d3.axisBottom(view));
  });
svg.call(zoom);
d3.select(host)
  .append("button")
  .attr("type", "button")
  .text("Reset zoom")
  .on("click", () => svg.call(zoom.transform, d3.zoomIdentity));
svg.call(zoom.transform, d3.zoomIdentity.translate(-60, 0).scale(2));
check(view.domain()[1] - view.domain()[0] < 10, "Zoom domain did not narrow");
check(base.domain().join(",") === "0,10", "Base scale mutated");
svg.call(zoom.transform, d3.zoomIdentity);
check(view.domain().join(",") === "0,10", "Reset failed");

output.textContent = "js-058 D3 complete";
console.log("js-058 D3 complete");
