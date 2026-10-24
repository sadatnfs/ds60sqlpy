// js-047: complete offline D3 browser reference.
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
  .attr("aria-label", "Axes, ticks, labels and numerical formatting")
  .style("width", "100%")
  .style("max-width", "640px");
svg.append("title").text("Axes, ticks, labels and numerical formatting");
const x = d3.scaleLinear().domain([0, 1]).range([70, 590]);
const axis = svg
  .append("g")
  .attr("transform", "translate(0,280)")
  .call(d3.axisBottom(x).tickValues([0, 0.25, 0.5, 0.75, 1]).tickFormat(d3.format(".0%")));
svg
  .append("text")
  .attr("x", 330)
  .attr("y", 330)
  .attr("text-anchor", "middle")
  .text("Conversion rate (fraction of eligible visits)");
svg.append("circle").attr("cx", x(0.25)).attr("cy", 200).attr("r", 10).attr("fill", "#be185d");
check(axis.selectAll(".tick").size() === 5, "Explicit tick count wrong");
check(
  axis
    .selectAll(".tick text")
    .nodes()
    .map((n) => n.textContent)
    .join(",") === "0%,25%,50%,75%,100%",
  "Percentage units wrong",
);

output.textContent = "js-047 D3 complete";
console.log("js-047 D3 complete");
