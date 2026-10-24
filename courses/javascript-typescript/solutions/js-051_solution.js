// js-051: complete offline D3 browser reference.
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
  .attr('aria-label', "Histograms, bin boundaries and distribution shape")
  .style('width', '100%')
  .style('max-width', '640px');
svg.append('title').text("Histograms, bin boundaries and distribution shape");
const values = [0, 2, 2, 4, 9, 10];
const bins = d3.bin().domain([0, 10]).thresholds([2, 4, 6, 8])(values);
const x = d3.scaleLinear().domain([0, 10]).range([60, 600]);
const y = d3.scaleLinear().domain([0, 3]).range([300, 30]);
svg
  .selectAll("rect")
  .data(bins)
  .join("rect")
  .attr("x", (d) => x(d.x0) + 1)
  .attr("width", (d) => Math.max(0, x(d.x1) - x(d.x0) - 2))
  .attr("y", (d) => y(d.length))
  .attr("height", (d) => y(0) - y(d.length))
  .attr("fill", "#0f766e");
svg.append("g").attr("transform", "translate(0,300)").call(d3.axisBottom(x));
svg.append("g").attr("transform", "translate(60,0)").call(d3.axisLeft(y).ticks(3));
check(bins.map((b) => b.length).join(",") === "1,2,1,0,2", "Boundary counts wrong");
check(d3.sum(bins, (b) => b.length) === values.length, "Histogram lost data");

output.textContent = "js-051 D3 complete";
console.log("js-051 D3 complete");
