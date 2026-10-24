// js-059: complete offline D3 browser reference.
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
  .attr("aria-label", "Hierarchies and tree layouts")
  .style("width", "100%")
  .style("max-width", "640px");
svg.append("title").text("Hierarchies and tree layouts");
const root = d3.hierarchy({
  name: "Learning",
  children: [
    { name: "Languages", children: [{ name: "JavaScript" }, { name: "Python" }] },
    { name: "Systems", children: [{ name: "Docker" }] },
  ],
});
d3.tree().size([260, 420])(root);
const g = svg.append("g").attr("transform", "translate(90,40)");
g.selectAll("path")
  .data(root.links())
  .join("path")
  .attr(
    "d",
    d3
      .linkHorizontal()
      .x((d) => d.y)
      .y((d) => d.x),
  )
  .attr("fill", "none")
  .attr("stroke", "#94a3b8");
const nodes = g
  .selectAll("g.node")
  .data(root.descendants())
  .join("g")
  .attr("class", "node")
  .attr("transform", (d) => `translate(${d.y},${d.x})`);
nodes.append("circle").attr("r", 6).attr("fill", "#2563eb");
nodes
  .append("text")
  .attr("x", (d) => (d.children ? -10 : 10))
  .attr("text-anchor", (d) => (d.children ? "end" : "start"))
  .attr("dy", ".35em")
  .text((d) => d.data.name);
check(root.descendants().length === 6 && root.links().length === 5, "Tree structure incorrect");
check(
  root.descendants().every((d) => Number.isFinite(d.x) && Number.isFinite(d.y)),
  "Nonfinite layout",
);

output.textContent = "js-059 D3 complete";
console.log("js-059 D3 complete");
