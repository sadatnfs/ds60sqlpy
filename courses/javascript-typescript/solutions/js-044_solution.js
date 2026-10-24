// js-044: complete offline D3 browser reference.
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
  .attr('aria-label', "Selections and data joins: enter, update and exit")
  .style('width', '100%')
  .style('max-width', '640px');
svg.append('title').text("Selections and data joins: enter, update and exit");
function draw(values) {
  check(
    values.every((v) => Number.isFinite(v) && v >= 0),
    "Invalid radius",
  );
  svg
    .selectAll("circle")
    .data(values)
    .join("circle")
    .attr("cx", (d, i) => 100 + i * 150)
    .attr("cy", 150)
    .attr("r", (d) => d)
    .attr("fill", "#7c3aed");
}
draw([20, 30, 40]);
draw([25, 35]);
check(svg.selectAll("circle").size() === 2, "Exit nodes were not removed");
check(
  svg
    .selectAll("circle")
    .nodes()
    .map((n) => +n.getAttribute("r"))
    .join(",") === "25,35",
  "Update values incorrect",
);
let refused = false;
try {
  draw([-1]);
} catch {
  refused = true;
}
check(refused, "Negative radius was not rejected");

output.textContent = "js-044 D3 complete";
console.log("js-044 D3 complete");
