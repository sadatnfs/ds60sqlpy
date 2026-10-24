// js-050: complete offline D3 browser reference.
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
  .attr('aria-label', "Scatterplots, size encodings and overplotting")
  .style('width', '100%')
  .style('max-width', '640px');
svg.append('title').text("Scatterplots, size encodings and overplotting");
const rows = [
  { id: "A", x: 1, y: 2, size: 1 },
  { id: "B", x: 2, y: 4, size: 4 },
  { id: "C", x: 3, y: 3, size: 2 },
];
const x = d3.scaleLinear().domain([0, 4]).range([60, 600]);
const y = d3.scaleLinear().domain([0, 5]).range([300, 30]);
const r = d3.scaleSqrt().domain([0, 4]).range([0, 24]);
svg
  .selectAll("circle")
  .data(rows, (d) => d.id)
  .join("circle")
  .attr("cx", (d) => x(d.x))
  .attr("cy", (d) => y(d.y))
  .attr("r", (d) => r(d.size))
  .attr("fill", "#7c3aed")
  .attr("fill-opacity", 0.65)
  .append("title")
  .text((d) => `${d.id}: x ${d.x}, y ${d.y}, size ${d.size}`);
svg.append("g").attr("transform", "translate(0,300)").call(d3.axisBottom(x));
svg.append("g").attr("transform", "translate(60,0)").call(d3.axisLeft(y));
check((r(4) * r(4)) / (r(1) * r(1)) === 4, "Area encoding wrong");
check(svg.selectAll("circle").size() === 3, "Record count wrong");

output.textContent = "js-050 D3 complete";
console.log("js-050 D3 complete");
