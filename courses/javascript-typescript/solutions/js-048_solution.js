// js-048: complete offline D3 browser reference.
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
  .attr("aria-label", "Data cleaning: CSV parsing, missing values and aggregation")
  .style("width", "100%")
  .style("max-width", "640px");
svg.append("title").text("Data cleaning: CSV parsing, missing values and aggregation");
const raw = d3.csvParse("category,value\nA,2\nA,3\nB,4\nB,\nC,oops");
const rejected = [];
const rows = raw.flatMap((r, i) => {
  const text = r.value.trim();
  const value = Number(text);
  if (text === "" || !Number.isFinite(value)) {
    rejected.push(i);
    return [];
  }
  return [{ category: r.category, value }];
});
const totals = Array.from(
  d3.rollup(
    rows,
    (g) => d3.sum(g, (d) => d.value),
    (d) => d.category,
  ),
  ([category, value]) => ({ category, value }),
);
svg
  .selectAll("rect")
  .data(totals)
  .join("rect")
  .attr("x", 100)
  .attr("y", (d, i) => 80 + i * 90)
  .attr("width", (d) => d.value * 70)
  .attr("height", 50)
  .attr("fill", "#0f766e");
svg
  .selectAll("text")
  .data(totals)
  .join("text")
  .attr("x", 20)
  .attr("y", (d, i) => 110 + i * 90)
  .text((d) => `${d.category}: ${d.value}`);
check(rows.length === 3 && rejected.length === 2, "Cleaning count incorrect");
check(totals[0].value === 5 && totals[1].value === 4, "Aggregation incorrect");

output.textContent = "js-048 D3 complete";
console.log("js-048 D3 complete");
