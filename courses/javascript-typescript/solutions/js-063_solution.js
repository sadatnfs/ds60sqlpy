// js-063: complete offline D3 browser reference.
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
  .attr('aria-label', "Choropleths, rate denominators and missing geographic joins")
  .style('width', '100%')
  .style('max-width', '640px');
svg.append('title').text("Choropleths, rate denominators and missing geographic joins");
const features = ["A", "B", "C"].map((id, i) => ({
  type: "Feature",
  id,
  properties: { name: id },
  geometry: {
    type: "Polygon",
    coordinates: [
      [
        [i * 170, 0],
        [i * 170 + 150, 0],
        [i * 170 + 150, 180],
        [i * 170, 180],
        [i * 170, 0],
      ],
    ],
  },
}));
const rows = [
  { id: "A", events: 10, total: 100 },
  { id: "B", events: 20, total: 100 },
];
check(new Set(rows.map((d) => d.id)).size === rows.length, "Duplicate region data");
const byId = new Map(rows.map((d) => [d.id, d.events / d.total]));
const color = d3.scaleSequential(d3.interpolateBlues).domain([0, 0.25]);
const path = d3.geoPath(d3.geoIdentity().translate([50, 70]));
svg
  .selectAll("path")
  .data(features, (d) => d.id)
  .join("path")
  .attr("d", path)
  .attr("fill", (d) => (byId.has(d.id) ? color(byId.get(d.id)) : "#d1d5db"))
  .attr("stroke", "#334155");
svg
  .selectAll("text")
  .data(features)
  .join("text")
  .attr("x", (d, i) => 80 + i * 170)
  .attr("y", 280)
  .text(
    (d) => `${d.id}: ${byId.has(d.id) ? d3.format(".0%")(byId.get(d.id)) : "missing"}`,
  );
check(byId.get("A") === 0.1 && byId.get("B") === 0.2, "Rates incorrect");
check(!byId.has("C"), "Missing region incorrectly filled");

output.textContent = "js-063 D3 complete";
console.log("js-063 D3 complete");
