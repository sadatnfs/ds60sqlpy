// js-055: complete offline D3 browser reference.
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
  .attr("aria-label", "Transitions, interruption and reduced-motion design")
  .style("width", "100%")
  .style("max-width", "640px");
svg.append("title").text("Transitions, interruption and reduced-motion design");
const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
const mark = svg
  .append("circle")
  .attr("cx", 80)
  .attr("cy", 160)
  .attr("r", 24)
  .attr("fill", "#7c3aed");
mark.interrupt("update");
await mark
  .transition("update")
  .duration(reduced ? 0 : 120)
  .attr("cx", 480)
  .end();
check(+mark.attr("cx") === 480, "Transition did not reach final state");
svg
  .append("text")
  .attr("x", 50)
  .attr("y", 280)
  .text(reduced ? "Immediate update: reduced motion requested" : "Bounded transition completed");

output.textContent = "js-055 D3 complete";
console.log("js-055 D3 complete");
