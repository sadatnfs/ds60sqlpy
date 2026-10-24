// js-057: complete offline D3 browser reference.
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
  .attr('aria-label', "Brushing and coordinated views")
  .style('width', '100%')
  .style('max-width', '640px');
svg.append('title').text("Brushing and coordinated views");
const rows = d3.range(1, 6).map((x) => ({ id: String(x), x }));
const x = d3.scaleLinear().domain([0, 6]).range([50, 590]);
const marks = svg
  .selectAll("circle")
  .data(rows)
  .join("circle")
  .attr("cx", (d) => x(d.x))
  .attr("cy", 150)
  .attr("r", 16);
const status = d3.select(host).append("p").attr("role", "status");
let selected = [];
const brush = d3
  .brushX()
  .extent([
    [50, 80],
    [590, 220],
  ])
  .on("brush end", (event) => {
    const range = event.selection?.map(x.invert);
    selected = range
      ? rows.filter((d) => d.x >= range[0] - 1e-9 && d.x <= range[1] + 1e-9)
      : rows;
    const ids = new Set(selected.map((d) => d.id));
    marks.attr("fill", (d) => (ids.has(d.id) ? "#2563eb" : "#cbd5e1"));
    status.text(`Selected: ${selected.map((d) => d.id).join(", ")}`);
  });
const layer = svg.append("g").call(brush);
d3.select(host)
  .append("button")
  .attr("type", "button")
  .text("Select 2 through 4")
  .on("click", () => layer.call(brush.move, [x(2), x(4)]));
d3.select(host)
  .append("button")
  .attr("type", "button")
  .text("Reset selection")
  .on("click", () => layer.call(brush.move, null));
layer.call(brush.move, [x(2), x(4)]);
check(selected.map((d) => d.id).join(",") === "2,3,4", "Brush data conversion wrong");

output.textContent = "js-057 D3 complete";
console.log("js-057 D3 complete");
