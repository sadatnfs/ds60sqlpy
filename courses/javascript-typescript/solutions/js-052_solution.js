// js-052: complete offline D3 browser reference.
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
  .attr("aria-label", "Statistical summaries, box plots and uncertainty intervals")
  .style("width", "100%")
  .style("max-width", "640px");
svg.append("title").text("Statistical summaries, box plots and uncertainty intervals");
const values = [1, 2, 3, 4, 5];
const q1 = d3.quantileSorted(values, 0.25),
  median = d3.quantileSorted(values, 0.5),
  q3 = d3.quantileSorted(values, 0.75);
const x = d3.scaleLinear().domain([0, 6]).range([60, 600]);
svg
  .append("line")
  .attr("x1", x(1))
  .attr("x2", x(5))
  .attr("y1", 150)
  .attr("y2", 150)
  .attr("stroke", "#334155");
svg
  .append("rect")
  .attr("x", x(q1))
  .attr("y", 110)
  .attr("width", x(q3) - x(q1))
  .attr("height", 80)
  .attr("fill", "#c4b5fd")
  .attr("stroke", "#5b21b6");
svg
  .append("line")
  .attr("x1", x(median))
  .attr("x2", x(median))
  .attr("y1", 110)
  .attr("y2", 190)
  .attr("stroke", "#1e293b")
  .attr("stroke-width", 3);
svg.append("g").attr("transform", "translate(0,260)").call(d3.axisBottom(x));
svg
  .append("text")
  .attr("x", 60)
  .attr("y", 40)
  .text("Observed values: 1, 2, 3, 4, 5; whiskers show min/max");
check(q1 === 2 && median === 3 && q3 === 4, "Quantiles incorrect");

output.textContent = "js-052 D3 complete";
console.log("js-052 D3 complete");
