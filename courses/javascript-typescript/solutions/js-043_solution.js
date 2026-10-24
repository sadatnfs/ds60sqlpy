// js-043: complete offline D3 browser reference.
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
  .attr('aria-label', "D3 and SVG: from a number to a visible mark")
  .style('width', '100%')
  .style('max-width', '640px');
svg.append('title').text("D3 and SVG: from a number to a visible mark");
const data = [
  { name: "A", value: 2 },
  { name: "B", value: 5 },
  { name: "C", value: 8 },
];
svg
  .selectAll("rect")
  .data(data)
  .join("rect")
  .attr("x", 100)
  .attr("y", (d, i) => 40 + i * 75)
  .attr("width", (d) => d.value * 20)
  .attr("height", 40)
  .attr("fill", "#2563eb");
svg
  .selectAll("text")
  .data(data)
  .join("text")
  .attr("x", 20)
  .attr("y", (d, i) => 65 + i * 75)
  .text((d) => `${d.name}: ${d.value}`);
check(svg.selectAll("rect").size() === 3, "Expected three bars");
check(
  svg
    .selectAll("rect")
    .nodes()
    .map((n) => +n.getAttribute("width"))
    .join(",") === "40,100,160",
  "Count-to-length mapping failed",
);

output.textContent = "js-043 D3 complete";
console.log("js-043 D3 complete");
