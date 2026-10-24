// js-066: complete offline D3 browser reference.
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
  .attr("aria-label", "D3 capstone: an accessible, tested analytical dashboard")
  .style("width", "100%")
  .style("max-width", "640px");
svg.append("title").text("D3 capstone: an accessible, tested analytical dashboard");
let chartWidth = Math.max(240, Math.min(host.clientWidth, 640));
svg.attr("viewBox", `0 0 ${chartWidth} 300`).style("font-size", "14px");
const rows = [
  { id: "A1", group: "A", hours: 3 },
  { id: "A2", group: "A", hours: 5 },
  { id: "B1", group: "B", hours: 4 },
  { id: "B2", group: "B", hours: 8 },
];
const original = JSON.stringify(rows);
check(new Set(rows.map((d) => d.id)).size === rows.length, "Duplicate IDs");
check(
  rows.every((d) => Number.isFinite(d.hours) && d.hours >= 0),
  "Invalid hours",
);
const summary = d3.select(host).append("p").attr("role", "status");
const label = d3.select(host).append("label").text("Learner group ");
const select = label.append("select").attr("aria-label", "Learner group");
select
  .selectAll("option")
  .data(["all", "A", "B"])
  .join("option")
  .attr("value", (d) => d)
  .text((d) => d);
const table = d3
  .select(host)
  .append("table")
  .style("width", "100%")
  .style("border-collapse", "collapse");
table.append("caption").text("Exact synthetic study hours");
const head = table.append("thead").append("tr");
head.append("th").attr("scope", "col").text("Record");
head.append("th").attr("scope", "col").text("Hours");
head
  .selectAll("th")
  .style("padding", ".35rem .6rem")
  .style("text-align", (d, i) => (i ? "right" : "left"))
  .style("border-bottom", "1px solid #cbd5e1");
const body = table.append("tbody");
function render(group) {
  const visible = rows
    .filter((d) => group === "all" || d.group === group)
    .slice()
    .sort((a, b) => b.hours - a.hours);
  const x = d3
    .scaleLinear()
    .domain([0, 10])
    .range([0, chartWidth - 120]);
  svg
    .selectAll("rect")
    .data(visible, (d) => d.id)
    .join("rect")
    .attr("x", 100)
    .attr("y", (d, i) => 30 + i * 65)
    .attr("width", (d) => x(d.hours))
    .attr("height", 38)
    .attr("fill", (d) => (d.group === "A" ? "#2563eb" : "#7c3aed"));
  svg
    .selectAll("text.label")
    .data(visible, (d) => d.id)
    .join("text")
    .attr("class", "label")
    .attr("x", 20)
    .attr("y", (d, i) => 55 + i * 65)
    .text((d) => `${d.id}: ${d.hours}`);
  const trs = body
    .selectAll("tr")
    .data(visible, (d) => d.id)
    .join("tr");
  trs
    .selectAll("td")
    .data((d) => [d.id, String(d.hours)])
    .join("td")
    .style("padding", ".3rem .6rem")
    .style("text-align", (d, i) => (i ? "right" : "left"))
    .text((d) => d);
  summary.text(`${visible.length} records; total ${d3.sum(visible, (d) => d.hours)} hours`);
  return visible;
}
select.on("change", (event) => render(event.target.value));
render("all");
check(summary.text() === "4 records; total 20 hours", "Baseline summary wrong");
select.property("value", "A").dispatch("change");
check(
  summary.text() === "2 records; total 8 hours" && svg.selectAll("rect").size() === 2,
  "Filter mismatch",
);
select.property("value", "all").dispatch("change");
check(
  body.selectAll("tr").size() === 4 && JSON.stringify(rows) === original,
  "Reset or source preservation failed",
);
d3.select(host)
  .append("p")
  .text("Synthetic study hours by learner group; this fixture is not a population estimate.");
let resizeFrame = 0;
const observer = new ResizeObserver(() => {
  if (resizeFrame !== 0) return;
  resizeFrame = requestAnimationFrame(() => {
    resizeFrame = 0;
    const next = Math.max(240, Math.min(host.clientWidth, 640));
    if (next !== chartWidth) {
      chartWidth = next;
      svg.attr("viewBox", `0 0 ${chartWidth} 300`);
      render(select.property("value"));
    }
  });
});
observer.observe(host);
addEventListener(
  "pagehide",
  () => {
    observer.disconnect();
    if (resizeFrame !== 0) cancelAnimationFrame(resizeFrame);
  },
  { once: true },
);

output.textContent = "js-066 D3 complete";
console.log("js-066 D3 complete");
