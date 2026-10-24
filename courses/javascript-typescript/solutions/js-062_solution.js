// js-062: complete offline D3 browser reference.
if (typeof d3 !== "object" || d3.version !== "7.9.0")
  throw new Error("Prepared D3 7.9.0 is required.");
const host = document.querySelector("#chart");
const output = document.querySelector("#output");
if (!host || !output) throw new Error("Preview chart/output nodes are required.");
host.replaceChildren();
const check = (condition, message) => {
  if (!condition) throw new Error(message);
};
const svg = d3
  .select(host)
  .append("svg")
  .attr("viewBox", "0 0 640 360")
  .attr("role", "img")
  .attr("aria-label", "Geographic data, GeoJSON and projection choices")
  .style("width", "100%")
  .style("max-width", "640px");
svg.append("title").text("Geographic data, GeoJSON and projection choices");
const data = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: { name: "West" },
      geometry: { type: "Point", coordinates: [-20, 10] },
    },
    {
      type: "Feature",
      properties: { name: "Center" },
      geometry: { type: "Point", coordinates: [0, 0] },
    },
    {
      type: "Feature",
      properties: { name: "East" },
      geometry: { type: "Point", coordinates: [20, 10] },
    },
  ],
};
const projection = d3.geoMercator().center([0, 0]).scale(400).translate([320, 190]);
const path = d3.geoPath(projection).pointRadius(8);
svg.selectAll("path").data(data.features).join("path").attr("d", path).attr("fill", "#2563eb");
svg
  .selectAll("text")
  .data(data.features)
  .join("text")
  .attr("x", (d) => projection(d.geometry.coordinates)[0] + 12)
  .attr("y", (d) => projection(d.geometry.coordinates)[1] + 4)
  .text((d) => d.properties.name);
const center = projection([0, 0]);
check(
  Math.abs(center[0] - 320) < 1e-9 && Math.abs(center[1] - 190) < 1e-9,
  "Projection anchor wrong",
);
check(svg.selectAll("path").size() === 3, "Feature count wrong");

output.textContent = "js-062 D3 complete";
console.log("js-062 D3 complete");
