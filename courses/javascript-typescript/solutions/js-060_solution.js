// js-060: complete offline D3 browser reference.
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
  .attr('aria-label', "Treemaps and area-based composition")
  .style('width', '100%')
  .style('max-width', '640px');
svg.append('title').text("Treemaps and area-based composition");
const root = d3
  .hierarchy({
    name: "Total",
    children: [
      { name: "Analysis", value: 6 },
      { name: "Engineering", value: 3 },
      { name: "Design", value: 1 },
    ],
  })
  .sum((d) => d.value || 0);
d3.treemap().size([540, 260]).padding(3)(root);
const cells = svg
  .append("g")
  .attr("transform", "translate(50,40)")
  .selectAll("g")
  .data(root.leaves(), (d) => d.data.name)
  .join("g")
  .attr("transform", (d) => `translate(${d.x0},${d.y0})`);
cells
  .append("rect")
  .attr("width", (d) => d.x1 - d.x0)
  .attr("height", (d) => d.y1 - d.y0)
  .attr("fill", (d, i) => ["#bfdbfe", "#c4b5fd", "#99f6e4"][i]);
cells
  .append("text")
  .attr("x", 8)
  .attr("y", 24)
  .text((d) => `${d.data.name}: ${d.value}`);
check(root.value === 10, "Hierarchy sum incorrect");
check(
  root.leaves().every((d) => d.x1 >= d.x0 && d.y1 >= d.y0),
  "Invalid treemap geometry",
);

output.textContent = "js-060 D3 complete";
console.log("js-060 D3 complete");
