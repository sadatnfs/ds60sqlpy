// js-053: complete offline D3 browser reference.
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
  .attr("aria-label", "Grouped and stacked bars: totals, composition and denominators")
  .style("width", "100%")
  .style("max-width", "640px");
svg.append("title").text("Grouped and stacked bars: totals, composition and denominators");
const rows = [
  { group: "X", a: 2, b: 3 },
  { group: "Y", a: 4, b: 2 },
];
const series = d3.stack().keys(["a", "b"])(rows);
const x = d3
  .scaleBand()
  .domain(rows.map((d) => d.group))
  .range([80, 580])
  .padding(0.3);
const y = d3.scaleLinear().domain([0, 7]).range([300, 30]);
svg
  .selectAll("g.series")
  .data(series)
  .join("g")
  .attr("class", "series")
  .attr("fill", (d, i) => ["#2563eb", "#f59e0b"][i])
  .selectAll("rect")
  .data((d) => d)
  .join("rect")
  .attr("x", (d) => x(d.data.group))
  .attr("y", (d) => y(d[1]))
  .attr("height", (d) => y(d[0]) - y(d[1]))
  .attr("width", x.bandwidth());
svg.append("g").attr("transform", "translate(0,300)").call(d3.axisBottom(x));
check(series[1][0][0] === 2 && series[1][0][1] === 5, "Stack endpoints wrong");
check(svg.selectAll("rect").size() === 4, "Segment count wrong");

output.textContent = "js-053 D3 complete";
console.log("js-053 D3 complete");
