// js-045: complete offline D3 browser reference.
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
  .attr('aria-label', "Keyed joins and object identity through updates")
  .style('width', '100%')
  .style('max-width', '640px');
svg.append('title').text("Keyed joins and object identity through updates");
function draw(rows) {
  check(new Set(rows.map((d) => d.id)).size === rows.length, "Duplicate keys");
  svg
    .selectAll("circle")
    .data(rows, (d) => d.id)
    .join("circle")
    .attr("data-id", (d) => d.id)
    .attr("cx", (d, i) => 150 + i * 250)
    .attr("cy", 150)
    .attr("r", (d) => d.v * 8)
    .attr("fill", "#0891b2");
}
draw([
  { id: "A", v: 3 },
  { id: "B", v: 5 },
]);
const before = svg.select('[data-id="A"]').node();
draw([
  { id: "B", v: 4 },
  { id: "A", v: 6 },
]);
check(svg.select('[data-id="A"]').node() === before, "A node identity changed");
check(+before.getAttribute("r") === 48, "A value did not update");
let rejected = false;
try {
  draw([
    { id: "A", v: 1 },
    { id: "A", v: 2 },
  ]);
} catch {
  rejected = true;
}
check(rejected, "Duplicate keys accepted");

output.textContent = "js-045 D3 complete";
console.log("js-045 D3 complete");
