// js-046: complete offline D3 browser reference.
if (typeof d3 !== 'object' || d3.version !== '7.9.0') throw new Error('Prepared D3 7.9.0 is required.');
const host = document.querySelector('#chart');
const output = document.querySelector('#output');
if (!host || !output) throw new Error('Preview chart/output nodes are required.');
host.replaceChildren();
const check = (condition, message) => { if (!condition) throw new Error(message); };
const svg = d3.select(host)
  .append('svg')
  .attr('viewBox', '0 0 640 360')
  .attr('role', 'img')
  .attr('aria-label', "Scales: domains, ranges, inversion and honest baselines")
  .style('width', '100%')
  .style('max-width', '640px');
svg.append('title').text("Scales: domains, ranges, inversion and honest baselines");
const rows = [
  { name: "A", value: 2 },
  { name: "B", value: 5 },
  { name: "C", value: 8 },
];
const x = d3
  .scaleBand()
  .domain(rows.map((d) => d.name))
  .range([60, 600])
  .padding(0.2);
const y = d3.scaleLinear().domain([0, 10]).range([300, 30]);
svg
  .selectAll("rect")
  .data(rows)
  .join("rect")
  .attr("x", (d) => x(d.name))
  .attr("y", (d) => y(d.value))
  .attr("width", x.bandwidth())
  .attr("height", (d) => y(0) - y(d.value))
  .attr("fill", "#2563eb");
check(y(0) === 300 && y(10) === 30, "Vertical direction wrong");
check(Math.abs(y.invert(y(5)) - 5) < 1e-10, "Scale inversion failed");
check(
  svg
    .selectAll("rect")
    .nodes()
    .every((n) => +n.getAttribute("height") > 0),
  "Bar heights must be positive",
);

output.textContent = "js-046 D3 complete";
console.log("js-046 D3 complete");
