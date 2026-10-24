// js-064: complete offline D3 browser reference.
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
  .attr("aria-label", "Canvas, rendering cost and spatial hit testing")
  .style("width", "100%")
  .style("max-width", "640px");
svg.append("title").text("Canvas, rendering cost and spatial hit testing");
svg.style("display", "none");
const canvas = document.createElement("canvas");
canvas.setAttribute("role", "img");
canvas.setAttribute("aria-label", "One hundred synthetic grid points");
host.prepend(canvas);
const ratio = Math.min(devicePixelRatio || 1, 2);
canvas.width = 600 * ratio;
canvas.height = 320 * ratio;
canvas.style.width = "100%";
canvas.style.maxWidth = "600px";
canvas.style.aspectRatio = "600 / 320";
const context = canvas.getContext("2d");
check(context, "Canvas2D unavailable");
context.setTransform(ratio, 0, 0, ratio, 0, 0);
const rows = d3
  .range(100)
  .map((i) => ({ id: i, x: 30 + (i % 10) * 58, y: 25 + Math.floor(i / 10) * 30 }));
context.fillStyle = "#2563eb";
for (const p of rows) {
  context.beginPath();
  context.arc(p.x, p.y, 4, 0, Math.PI * 2);
  context.fill();
}
const tree = d3
  .quadtree()
  .x((d) => d.x)
  .y((d) => d.y)
  .addAll(rows);
check(tree.find(31, 26).id === 0, "Spatial lookup wrong");
check(rows.length === 100, "Grid count wrong");
d3.select(host)
  .append("p")
  .text("100 synthetic points on a 10 by 10 grid. Nearest to (31,26): record 0.");

output.textContent = "js-064 D3 complete";
console.log("js-064 D3 complete");
