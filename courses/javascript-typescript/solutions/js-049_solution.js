// js-049: complete offline D3 browser reference.
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
  .attr("aria-label", "Time series: dates, sorted lines and visible gaps")
  .style("width", "100%")
  .style("max-width", "640px");
svg.append("title").text("Time series: dates, sorted lines and visible gaps");
const rows = [
  { date: new Date("2024-01-03T00:00:00Z"), value: null },
  { date: new Date("2024-01-01T00:00:00Z"), value: 2 },
  { date: new Date("2024-01-02T00:00:00Z"), value: 4 },
  { date: new Date("2024-01-04T00:00:00Z"), value: 3 },
  { date: new Date("2024-01-05T00:00:00Z"), value: 5 },
].sort((a, b) => a.date - b.date);
const x = d3
  .scaleUtc()
  .domain(d3.extent(rows, (d) => d.date))
  .range([60, 600]);
const y = d3.scaleLinear().domain([0, 6]).range([280, 30]);
const line = d3
  .line()
  .defined((d) => d.value !== null && Number.isFinite(d.value))
  .x((d) => x(d.date))
  .y((d) => y(d.value));
const path = line(rows);
svg
  .append("path")
  .attr("d", path)
  .attr("fill", "none")
  .attr("stroke", "#2563eb")
  .attr("stroke-width", 3);
svg
  .append("g")
  .attr("transform", "translate(0,280)")
  .call(d3.axisBottom(x).ticks(d3.utcDay.every(1)).tickFormat(d3.utcFormat("%b %d")));
check(rows[0].date.toISOString() === "2024-01-01T00:00:00.000Z", "Dates not sorted");
check((path.match(/M/g) || []).length === 2, "Missing value did not split line");

output.textContent = "js-049 D3 complete";
console.log("js-049 D3 complete");
