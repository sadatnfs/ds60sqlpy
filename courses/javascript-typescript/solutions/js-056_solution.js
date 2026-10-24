// js-056: complete offline D3 browser reference.
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
  .attr('aria-label', "Pointer interaction, keyboard access and safe tooltips")
  .style('width', '100%')
  .style('max-width', '640px');
svg.append('title').text("Pointer interaction, keyboard access and safe tooltips");
const rows = [
  { id: "A", value: 3 },
  { id: "B", value: 7 },
];
const status = d3
  .select(host)
  .append("p")
  .attr("role", "status")
  .attr("aria-live", "polite");
const marks = svg
  .selectAll("circle")
  .data(rows, (d) => d.id)
  .join("circle")
  .attr("cx", (d, i) => 180 + i * 260)
  .attr("cy", 150)
  .attr("r", (d) => d.value * 5)
  .attr("fill", "#0891b2");
function selectRow(row) {
  status.text(`${row.id}: ${row.value}`);
  marks
    .attr("stroke", (d) => (d.id === row.id ? "#111827" : "none"))
    .attr("stroke-width", 3);
}
marks.on("pointerenter", (event, d) => selectRow(d));
const controls = d3.select(host).append("div");
const buttons = controls
  .selectAll("button")
  .data(rows)
  .join("button")
  .attr("type", "button")
  .text((d) => `Inspect ${d.id}`)
  .on("click", (event, d) => selectRow(d));
buttons.nodes()[1].click();
check(status.text() === "B: 7", "Native control did not select B");
check(
  buttons.nodes().every((n) => n instanceof HTMLButtonElement),
  "Expected native buttons",
);

output.textContent = "js-056 D3 complete";
console.log("js-056 D3 complete");
