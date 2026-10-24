// js-061: complete offline D3 browser reference.
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
  .attr('aria-label', "Networks, force simulation and reproducible layouts")
  .style('width', '100%')
  .style('max-width', '640px');
svg.append('title').text("Networks, force simulation and reproducible layouts");
const sourceNodes = [{ id: "A" }, { id: "B" }, { id: "C" }];
const nodes = sourceNodes.map((d) => ({ ...d }));
const links = [
  { source: "A", target: "B" },
  { source: "B", target: "C" },
  { source: "C", target: "A" },
];
const simulation = d3
  .forceSimulation(nodes)
  .randomSource(d3.randomLcg(0.5))
  .force(
    "link",
    d3
      .forceLink(links)
      .id((d) => d.id)
      .distance(140),
  )
  .force("charge", d3.forceManyBody().strength(-150))
  .force("center", d3.forceCenter(320, 170))
  .stop();
simulation.tick(100);
svg
  .selectAll("line")
  .data(links)
  .join("line")
  .attr("x1", (d) => d.source.x)
  .attr("y1", (d) => d.source.y)
  .attr("x2", (d) => d.target.x)
  .attr("y2", (d) => d.target.y)
  .attr("stroke", "#94a3b8");
svg
  .selectAll("circle")
  .data(nodes, (d) => d.id)
  .join("circle")
  .attr("cx", (d) => d.x)
  .attr("cy", (d) => d.y)
  .attr("r", 18)
  .attr("fill", "#f59e0b");
svg
  .selectAll("text")
  .data(nodes)
  .join("text")
  .attr("x", (d) => d.x)
  .attr("y", (d) => d.y + 5)
  .attr("text-anchor", "middle")
  .text((d) => d.id);
check(
  nodes.every((d) => Number.isFinite(d.x) && Number.isFinite(d.y)),
  "Simulation positions invalid",
);
check(
  sourceNodes.every((d) => !("x" in d)),
  "Original source mutated",
);
check(
  links.every((d) => typeof d.source === "object" && typeof d.target === "object"),
  "Links unresolved",
);

output.textContent = "js-061 D3 complete";
console.log("js-061 D3 complete");
