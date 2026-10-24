"""Original D3 visualization teaching specifications and offline references."""

LESSONS = []


def add(title, concepts, mental, anatomy, a, b, tasks, reference, *refs):
    assert len(tasks) == 6
    LESSONS.append((title, concepts, mental, anatomy, [a, b], tasks, reference, refs))


add(
    "D3 and SVG: from a number to a visible mark",
    ["SVG", "viewBox", "selection", "visual encoding"],
    """D3 is a collection of JavaScript tools for transforming data and connecting it to visual output. It does not choose a correct chart or statistical question for you. A visual encoding maps a data property to a perceptual property such as position, length, area or color. Begin by naming the quantity and units before choosing a mark.

SVG is a document tree of vector shapes. A rectangle has x and y coordinates, width and height. In the usual SVG coordinate system x increases to the right and y increases downward. A viewBox describes the internal coordinate system; CSS controls how that system fits the available display area. A shape can be present in the DOM while lying outside the visible viewBox.

The first chart maps three synthetic counts to horizontal bar lengths. A zero-length bar corresponds to zero, making length comparisons interpretable. Labels provide category identity and exact values. The chart is intentionally small enough that you can calculate every coordinate by hand.""",
    """`d3.select(host)` wraps one existing DOM element in a selection. `.append('svg')` creates an SVG child and returns a selection containing it. `.attr(name, value)` changes an attribute; a callback receives the bound datum and index. A chain is a sequence of operations, not special chart syntax.

This lesson first uses a simple multiplier rather than a scale to expose the arithmetic. With width equal to count times 20, counts 2, 5 and 8 produce widths 40, 100 and 160. Later lessons replace the literal multiplier with a scale whose domain and range are explicit. Keep text separate from rectangle geometry.""",
    (
        "Map a count to length",
        "A literal computation exposes the first encoding.",
        "const count = 5;\nconst width = count * 20;\nconsole.log(width);",
        "100 SVG coordinate units.",
    ),
    (
        "Remember SVG vertical direction",
        "These two centers have increasing y downward.",
        "const centers = [{x: 40, y: 30}, {x: 40, y: 80}];\nconsole.log(centers[1].y > centers[0].y);",
        "The second point is lower, even though its y value is larger.",
    ),
    [
        (
            "Predict the three bar widths.",
            "40, 100 and 160 units.",
            "The same linear multiplier maps all counts. A consistent baseline makes the length ratio represent the count ratio.",
        ),
        (
            "Change the multiplier to 10.",
            "All widths halve while category values remain unchanged.",
            "This changes display geometry, not the data. Keep labels and the explanation of units consistent.",
        ),
        (
            "Create three labeled bars from a saved blank pad.",
            "Exactly three rectangles with matching labels and counts.",
            "Use a small input array and inspect mark count before styling. Every record should have a visible representation.",
        ),
        (
            "Diagnose a rectangle outside the viewBox.",
            "Its DOM presence differs from its visible intersection.",
            "Inspect coordinates and viewBox bounds. Adding another append does not repair a coordinate error.",
        ),
        (
            "Add a zero-count category.",
            "A zero-length bar with a visible category/value label.",
            "Zero is data, not missingness. Keep its label so the absence of length has an explicit interpretation.",
        ),
        (
            "Explain why position and length suit count comparison.",
            "A common baseline supports meaningful magnitude comparison.",
            "Choose the encoding to match the task. Area and decorative shapes can make a simple comparison harder.",
        ),
    ],
    r"""
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
""",
    "https://d3js.org/d3-selection/selecting",
    "https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/viewBox",
)

add(
    "Selections and data joins: enter, update and exit",
    ["selection", "data join", "enter", "exit"],
    """A selection is a group of DOM nodes, not a copy of their HTML. A data join relates an array of records to selected nodes. Records without corresponding nodes enter; nodes with corresponding records update; surplus nodes exit. This makes repeated rendering a reconciliation operation rather than an instruction to append duplicates forever.

The selector describes the nodes you intend to manage. `selectAll('circle')` can begin empty; the subsequent data join creates the required nodes. `join('circle')` handles the common enter/update/exit case. Attribute callbacks then assign geometry from each bound record.

A render function should produce the intended state when called again. Calling append for every record on every update leaves stale marks and inflates counts. Start with a small sequence, such as three values followed by two, and verify both node count and attributes after the second render.""",
    """`selection.data(values).join('circle')` binds the current values and returns the merged entered/updated selection. Without a key, matching is by index within a group. This can be correct when positions are identities, but the next lesson shows why stable entity IDs often need keys.

An attribute callback `(d, i) => ...` receives the record as d and its current group index as i. Returning undefined for a required coordinate can remove or invalidate the intended attribute. Inspect the derived values before blaming SVG rendering.""",
    (
        "Reconcile a changing count",
        "This fragment assumes an existing svg selection.",
        'function draw(values) {\n  svg.selectAll("circle").data(values).join("circle").attr("r", d => d);\n}\ndraw([5, 10, 15]);\ndraw([8, 12]);',
        "Two circles remain; their radii are 8 and 12.",
    ),
    (
        "Contrast unconditional append",
        "This is the bug to reason about, not the reference strategy.",
        'for (const value of [5, 10]) {\n  svg.append("circle").attr("r", value);\n}',
        "Calling this loop twice creates four circles because it does not reconcile existing nodes.",
    ),
    [
        (
            "Predict the node count after two draws.",
            "Two circles after changing three records to two.",
            "The exit selection is removed by the standard join. Repeated rendering should reflect current input cardinality.",
        ),
        (
            "Change the second input to an empty array.",
            "No managed circles remain.",
            "An empty dataset is a valid state. Exit handling should remove old marks rather than showing stale data.",
        ),
        (
            "Write a render function using a data join.",
            "Repeated calls produce exactly one mark per current record.",
            "Separate creation policy from attributes so the function can update existing nodes instead of appending duplicates.",
        ),
        (
            "Diagnose a chart that doubles its nodes on every click.",
            "It uses unconditional append or selects the wrong managed nodes.",
            "Check the selector and join boundary first. Styling cannot correct an ever-growing stale DOM.",
        ),
        (
            "Add an explicit invalid-value rejection.",
            "A negative radius input is refused before drawing.",
            "Geometry has a domain contract. Silent invalid attributes make a bad input look like a missing data point.",
        ),
        (
            "Apply the same pattern to an HTML list.",
            "Current records reconcile to current list items.",
            "The mechanism is about data-to-node relationships, not SVG alone. Preserve text safety when labels are external.",
        ),
    ],
    r"""
function draw(values) {
  check(
    values.every((v) => Number.isFinite(v) && v >= 0),
    "Invalid radius",
  );
  svg
    .selectAll("circle")
    .data(values)
    .join("circle")
    .attr("cx", (d, i) => 100 + i * 150)
    .attr("cy", 150)
    .attr("r", (d) => d)
    .attr("fill", "#7c3aed");
}
draw([20, 30, 40]);
draw([25, 35]);
check(svg.selectAll("circle").size() === 2, "Exit nodes were not removed");
check(
  svg
    .selectAll("circle")
    .nodes()
    .map((n) => +n.getAttribute("r"))
    .join(",") === "25,35",
  "Update values incorrect",
);
let refused = false;
try {
  draw([-1]);
} catch {
  refused = true;
}
check(refused, "Negative radius was not rejected");
""",
    "https://d3js.org/d3-selection/joining",
)

add(
    "Keyed joins and object identity through updates",
    ["key", "identity", "ordering", "reconciliation"],
    """A key identifies the same entity across different arrays. It should be stable and unique within the joined group. An array index identifies a position, which can change after sorting or filtering. Confusing identity with position can attach the wrong interaction state or transition to a record.

A keyed join lets a DOM node continue representing the same entity even when the record order changes. The node can receive new values while preserving its identity. Exit removes entities no longer present; enter adds new identities. This is especially important for animated updates and keyboard focus.

Duplicate keys violate the intended one-entity-one-node relationship. D3 has defined matching behavior, but relying on it to silently fix bad input is a poor data contract. Validate uniqueness before drawing and decide explicitly whether repeated categories should be aggregated or represented by distinct IDs.""",
    """Use `.data(records, d => d.id)` to match by identity. Save a node reference for entity A, reorder the records and redraw, then compare with `===`. This checks actual DOM reuse, not just a similar-looking chart.

Sort a copied array when you want display order without mutating a source collection owned elsewhere. Keep the key based on identity rather than the value being sorted. A value can change while the entity remains the same.""",
    (
        "Match by stable ID",
        "The key does not depend on array position.",
        'svg.selectAll("circle").data([{id:"A",v:2},{id:"B",v:4}], d=>d.id).join("circle");',
        "One node per ID, with identity available across later updates.",
    ),
    (
        "Reject duplicate identity",
        "A short check makes the assumption inspectable.",
        'const rows = [{id:"A"},{id:"A"}];\nconst unique = new Set(rows.map(d=>d.id)).size === rows.length;\nconsole.log(unique);',
        "false; decide how to repair the input rather than drawing ambiguous entities.",
    ),
    [
        (
            "Predict which node should survive reordering.",
            "The node for A remains the same object.",
            "Keys express entity identity. Reordering changes placement, not which object the node represents.",
        ),
        (
            "Update A value while retaining its ID.",
            "The existing A node receives new geometry.",
            "An entity can change attributes without being replaced. This distinction supports coherent transitions and focus behavior.",
        ),
        (
            "Implement a keyed redraw with two records.",
            "Node identity and current data values both match expectations.",
            "Test object equality as well as visible geometry. A fresh identical-looking node would not prove the reuse contract.",
        ),
        (
            "Diagnose using a sorted index as the key.",
            "Position changes can associate a node with a different entity.",
            "The bug may be invisible until stateful interactions or animation are added. Choose an ID independent of ordering.",
        ),
        (
            "Reject duplicate IDs before rendering.",
            "A clear error precedes ambiguous joins.",
            "Validation belongs near the data boundary. If duplicates are legitimate, define an aggregation or a composite identity deliberately.",
        ),
        (
            "Transfer identity reasoning to a live leaderboard.",
            "Scores change and ranks reorder while participant IDs remain stable.",
            "The chart should show movement of known participants rather than replacement of anonymous ranked positions.",
        ),
    ],
    r"""
function draw(rows) {
  check(new Set(rows.map((d) => d.id)).size === rows.length, "Duplicate keys");
  svg
    .selectAll("circle")
    .data(rows, (d) => d.id)
    .join("circle")
    .attr("data-id", (d) => d.id)
    .attr("cx", (d, i) => 150 + i * 250)
    .attr("cy", 150)
    .attr("r", (d) => d.v * 8)
    .attr("fill", "#0891b2");
}
draw([
  { id: "A", v: 3 },
  { id: "B", v: 5 },
]);
const before = svg.select('[data-id="A"]').node();
draw([
  { id: "B", v: 4 },
  { id: "A", v: 6 },
]);
check(svg.select('[data-id="A"]').node() === before, "A node identity changed");
check(+before.getAttribute("r") === 48, "A value did not update");
let rejected = false;
try {
  draw([
    { id: "A", v: 1 },
    { id: "A", v: 2 },
  ]);
} catch {
  rejected = true;
}
check(rejected, "Duplicate keys accepted");
""",
    "https://d3js.org/d3-selection/joining",
)

add(
    "Scales: domains, ranges, inversion and honest baselines",
    ["domain", "range", "linear scale", "band scale"],
    """A scale maps values from a data domain to a visual range. A linear scale preserves proportional differences: equal changes in input produce equal changes in output. The domain is expressed in data units, while the range can be pixels or SVG coordinates. Mixing those spaces is a common source of invisible or misleading marks.

A vertical quantitative scale often has range `[bottom, top]` because SVG y increases downward. This reversal makes larger values appear higher. A band scale maps categories to discrete bands and provides a bandwidth for bars. The category order is an explicit design decision.

Bars encode magnitude by length, so a zero baseline is usually essential. A line chart can sometimes use a narrower vertical domain if the axis clearly communicates it and the analytical purpose warrants it. Log scales require positive values in an ordinary positive domain; zero cannot be inserted casually. Explain the scale choice as part of the claim.""",
    """A linear scale is callable: `x(5)` returns a coordinate. Its `.invert(pixel)` maps a coordinate back to data, useful for interactions. `.clamp(true)` bounds output to the range but can hide out-of-domain values if used without a clear policy. `.nice()` adjusts domain endpoints for readable ticks; it does not modify the raw data.

For the example, domain `[0,10]` and range `[40,600]` maps 0 to 40, 5 to 320 and 10 to 600. The zero-origin formula is simple enough to check by hand before relying on the library.""",
    (
        "Calculate and invert",
        "The midpoint maps to the visual midpoint.",
        "const x=d3.scaleLinear().domain([0,10]).range([40,600]);\nconsole.log(x(5), x.invert(320));",
        "320 and 5.",
    ),
    (
        "Lay out categories",
        "A band scale allocates positions and width together.",
        'const x=d3.scaleBand().domain(["A","B","C"]).range([40,600]).padding(0.2);\nconsole.log(x("A") < x("B"), x.bandwidth() > 0);',
        "Both comparisons are true; an unknown category returns undefined.",
    ),
    [
        (
            "Predict midpoint and endpoint positions.",
            "0 maps to 40, 5 to 320 and 10 to 600.",
            "The scale maps data space into visual space. These exact cases catch a reversed or incorrectly offset range.",
        ),
        (
            "Reverse a vertical range.",
            "Higher values move upward in SVG coordinates.",
            "The data order stays the same while the coordinate direction reverses. Explain this before changing bar y and height formulas.",
        ),
        (
            "Build a scale-based bar chart.",
            "Bar geometry derives from a zero baseline and a named domain.",
            "Use y(0)-y(value) for positive bar height rather than treating a coordinate as a magnitude.",
        ),
        (
            "Diagnose using y(value) as bar height.",
            "Position and length were confused.",
            "A vertical coordinate measures from the SVG origin. A bar height measures the distance from its baseline.",
        ),
        (
            "Handle an unknown band category.",
            "Reject or explicitly extend the domain rather than emit undefined geometry.",
            "An undefined mapping should not silently remove a category. Keep the category domain aligned with the intended dataset.",
        ),
        (
            "Defend a scale choice for signed residuals.",
            "A diverging domain with visible zero and explicit units.",
            "Scale design should expose the analytical reference point. A zero baseline has a different role for signed residual position than for positive bar length.",
        ),
    ],
    r"""
const rows = [
  { name: "A", value: 2 },
  { name: "B", value: 5 },
  { name: "C", value: 8 },
];
const x = d3
  .scaleBand()
  .domain(rows.map((d) => d.name))
  .range([60, 600])
  .padding(0.2);
const y = d3.scaleLinear().domain([0, 10]).range([300, 30]);
svg
  .selectAll("rect")
  .data(rows)
  .join("rect")
  .attr("x", (d) => x(d.name))
  .attr("y", (d) => y(d.value))
  .attr("width", x.bandwidth())
  .attr("height", (d) => y(0) - y(d.value))
  .attr("fill", "#2563eb");
check(y(0) === 300 && y(10) === 30, "Vertical direction wrong");
check(Math.abs(y.invert(y(5)) - 5) < 1e-10, "Scale inversion failed");
check(
  svg
    .selectAll("rect")
    .nodes()
    .every((n) => +n.getAttribute("height") > 0),
  "Bar heights must be positive",
);
""",
    "https://d3js.org/d3-scale/linear",
    "https://d3js.org/d3-scale/band",
)

add(
    "Axes, ticks, labels and numerical formatting",
    ["axis", "tick", "format", "units"],
    """An axis makes a scale interpretable by displaying reference positions and labels. D3 axis generators create SVG elements from a scale; they do not choose the right statistical units or description. The chart author must name the quantity and make tick formatting consistent with the values.

Ticks are selected reference values, not necessarily every data point. A requested tick count is often a hint rather than an exact guarantee. Explicit tick values are useful for small controlled examples. Formatting changes displayed text, not the underlying numeric scale.

Percent data illustrates a common mistake. A formatter expecting fractions displays 0.25 as 25%. If the data is already 25 and you apply that formatter, it displays 2500%. Keep the stored representation, axis label and annotation units aligned. Precision should communicate measurement meaning rather than decorate every value with many decimals.""",
    """Call an axis generator on a group: `g.call(d3.axisBottom(x))`. Translate that group to the bottom coordinate, leaving the scale range in the chart’s coordinate system. Recalling the generator on the same group updates its ticks.

Use a visible axis title and a chart description. Avoid assuming that a bare dollar sign, abbreviation or color legend communicates enough context. Units and denominator matter, especially for rates and normalized comparisons.""",
    (
        "Format fractions as percentages",
        "The number remains a fraction internally.",
        'const percent=d3.format(".0%");\nconsole.log(percent(0.25), percent(25));',
        "25% and 2500%, revealing the representation mismatch.",
    ),
    (
        "Use explicit ticks for a teaching chart",
        "The same scale drives marks and axis.",
        'const x=d3.scaleLinear().domain([0,10]).range([60,600]);\nsvg.append("g").attr("transform","translate(0,300)").call(d3.axisBottom(x).tickValues([0,5,10]));',
        "Three labeled tick positions align with the scale endpoints and midpoint.",
    ),
    [
        (
            "Predict percent formatting for 0.4.",
            "40%.",
            "The format treats the input as a fraction. It scales displayed text without changing the data domain.",
        ),
        (
            "Change explicit tick values to four named values.",
            "The axis labels match that list and remain aligned with the marks.",
            "Tick selection is a presentation decision. Keep the scale shared so a separate formatting change does not shift data positions.",
        ),
        (
            "Build a labeled quantitative axis.",
            "Visible quantity, units and correctly formatted tick values.",
            "A reader should understand what a coordinate means without opening the source code.",
        ),
        (
            "Diagnose 2500% for a value intended as 25%.",
            "The stored percentage was treated as a fraction.",
            "Repair the representation contract at the data boundary or choose a formatter matching stored units. Do not merely remove the percent sign.",
        ),
        (
            "Compare fixed precision and meaningful precision.",
            "Displayed digits reflect measurement and comparison needs.",
            "More decimals are not more accuracy. Choose enough precision to avoid hiding meaningful differences without implying unsupported measurement certainty.",
        ),
        (
            "Design axes for counts and rates side by side.",
            "Separate unit labels and denominators make the comparison explicit.",
            "A count and a rate answer different questions. Shared colors do not make their numeric scales interchangeable.",
        ),
    ],
    r"""
const x = d3.scaleLinear().domain([0, 1]).range([70, 590]);
const axis = svg
  .append("g")
  .attr("transform", "translate(0,280)")
  .call(
    d3.axisBottom(x).tickValues([0, 0.25, 0.5, 0.75, 1]).tickFormat(d3.format(".0%")),
  );
svg
  .append("text")
  .attr("x", 330)
  .attr("y", 330)
  .attr("text-anchor", "middle")
  .text("Conversion rate (fraction of eligible visits)");
svg
  .append("circle")
  .attr("cx", x(0.25))
  .attr("cy", 200)
  .attr("r", 10)
  .attr("fill", "#be185d");
check(axis.selectAll(".tick").size() === 5, "Explicit tick count wrong");
check(
  axis
    .selectAll(".tick text")
    .nodes()
    .map((n) => n.textContent)
    .join(",") === "0%,25%,50%,75%,100%",
  "Percentage units wrong",
);
""",
    "https://d3js.org/d3-axis",
    "https://d3js.org/d3-format",
)

add(
    "Data cleaning: CSV parsing, missing values and aggregation",
    ["CSV", "validation", "missingness", "rollup"],
    """CSV is a text format whose cells do not automatically have the domain types your analysis needs. Parsing a file into rows and interpreting strings as numbers or dates are separate steps. Empty strings, malformed values and duplicate IDs require explicit policies before visual encoding.

A missing measurement is not necessarily zero. Replacing absence with zero can distort averages, totals and visual trends. Reject invalid rows with a reason, retain a count of excluded rows, and make the policy visible to the chart reader. Trimming text and checking finite numeric values are small but important boundary operations.

Aggregation changes the row grain. A transaction table has one row per event; a category summary may have one row per group. The correct denominator and missing-value policy depend on that grain. A data scientist should be able to reconstruct the aggregate from the small source rows before rendering it.""",
    """`d3.csvParse` parses inline CSV without a network request. A row accessor can return a cleaned object or null to omit a row, but an omission should be counted and explained. `Number('')` is zero, which is why a blank-string check must precede numeric conversion.

`d3.rollup(rows, group => d3.sum(group, d => d.value), d => d.category)` returns a Map keyed by category. The grouping key should be normalized intentionally. Case-sensitive category names may be genuinely distinct or accidental inconsistencies; do not merge them without a domain decision.""",
    (
        "Reject blank and malformed numbers",
        "This function separates missingness from numeric conversion.",
        'function numberOrNull(text){\n  if(text.trim()==="") return null;\n  const n=Number(text); return Number.isFinite(n)?n:null;\n}\nconsole.log(numberOrNull(""),numberOrNull("3"),numberOrNull("oops"));',
        "null, 3, null.",
    ),
    (
        "Aggregate a known grain",
        "Each input row is one event.",
        'const totals=d3.rollup([{g:"A",v:2},{g:"A",v:3},{g:"B",v:4}], rows=>d3.sum(rows,d=>d.v), d=>d.g);\nconsole.log(totals.get("A"));',
        "5, from exactly two A events.",
    ),
    [
        (
            "Predict blank-string numeric conversion.",
            "Number of an empty string is 0, so prevalidation is required.",
            "Blind conversion silently changes missingness into a measured zero. Keep those states distinct.",
        ),
        (
            "Count rejected rows with reasons.",
            "Every omitted row is accounted for as blank or malformed.",
            "A chart should not silently shrink its sample. A small rejection ledger makes the cleaning policy reviewable.",
        ),
        (
            "Parse and aggregate the inline fixture.",
            "A totals to 5 and B totals to 4 from valid rows.",
            "Check the row-level interpretation before grouping. Aggregation can conceal a wrong conversion if only the final shape is inspected.",
        ),
        (
            "Diagnose treating a blank value as zero.",
            "The chart includes an invented measurement.",
            "Repair the cleaning rule and compare the resulting counts or means. Merely hiding the zero mark does not fix the data.",
        ),
        (
            "Handle a category with only missing rows.",
            "Its absence or missing state is documented rather than called zero.",
            "Whether to retain an empty category depends on the analytical universe. Make that decision explicit.",
        ),
        (
            "Transfer the pipeline to a rate metric.",
            "Validate numerator and denominator at a defined grain before division.",
            "Averaging percentages can differ from a ratio of sums. Choose the aggregation that matches the question.",
        ),
    ],
    r"""
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
""",
    "https://d3js.org/d3-dsv",
    "https://d3js.org/d3-array/group",
)

add(
    "Time series: dates, sorted lines and visible gaps",
    ["UTC", "time scale", "line generator", "missing interval"],
    """A time series associates measurements with times. A JavaScript Date represents an instant, while formatting can use local time or UTC. If the lesson uses UTC dates, use UTC parsing, scales and formatting consistently so a chart does not shift a day in another time zone.

A line connects observations in the supplied order. D3 does not automatically sort your records by time. Connecting unsorted points can produce a zigzag that implies a path the data never took. Sorting a copy preserves the source order when other code owns the original data.

Missing intervals deserve visible treatment. A line generator’s defined predicate can break a path at missing observations. Connecting across a long outage can imply continuous measurement when none exists. Explain whether a gap means missing data, no activity or a deliberate sampling interval.""",
    """`d3.scaleUtc` maps instants to x positions. A line generator uses x and y accessors to produce an SVG path string. `.defined(d => Number.isFinite(d.value))` controls which records form continuous segments. Set `fill: none` for an ordinary line so the path is not treated as a filled polygon.

A null value must be rejected explicitly because `Number(null)` becomes zero. Sorting and missingness policies are data decisions, not merely chart styling. The reference checks ordering and the number of separate path segments in a small fixture.""",
    (
        "Use explicit UTC instants",
        "The Z suffix makes the time zone unambiguous.",
        'const a=new Date("2024-01-01T00:00:00Z");\nconst b=new Date("2024-01-02T00:00:00Z");\nconsole.log((b-a)/86400000);',
        "1 day for these two instants.",
    ),
    (
        "Break a line at missing data",
        "This fragment uses already defined x and y scales.",
        "const line=d3.line().defined(d=>d.value!==null).x(d=>x(d.date)).y(d=>y(d.value));",
        "A null observation splits the line instead of drawing a false zero or connecting through it.",
    ),
    [
        (
            "Predict date order after sorting.",
            "Chronological order by numeric instant.",
            "The line generator uses array order. Sorting is an explicit preprocessing step rather than a hidden property of time scales.",
        ),
        (
            "Insert a missing observation.",
            "The path has a visible gap under the stated policy.",
            "A missing value is not a measured zero. Preserve enough records to represent the missing interval.",
        ),
        (
            "Build a UTC line chart with a gap.",
            "Time-ordered points and separate defined segments.",
            "Use matching time parsing, scale and formatting conventions. Check the data ordering independently of the rendered path.",
        ),
        (
            "Diagnose a line that doubles back in time.",
            "Input order is unsorted or dates were parsed incorrectly.",
            "Inspect numeric timestamps before changing interpolation. A curve style cannot repair incorrect temporal ordering.",
        ),
        (
            "Handle an empty or all-missing series.",
            "Show an explicit no-data message rather than invalid domains.",
            "Extent on no valid data does not define a meaningful chart scale. Make the empty state part of the component contract.",
        ),
        (
            "Explain interpolation limits for irregular observations.",
            "Connecting samples is a visual assumption, not evidence between measurements.",
            "Label gaps and sampling intervals. A smooth curve can suggest precision or continuity the data does not support.",
        ),
    ],
    r"""
const rows = [
  { date: new Date("2024-01-03T00:00:00Z"), value: null },
  { date: new Date("2024-01-01T00:00:00Z"), value: 2 },
  { date: new Date("2024-01-02T00:00:00Z"), value: 4 },
  { date: new Date("2024-01-04T00:00:00Z"), value: 3 },
  { date: new Date("2024-01-05T00:00:00Z"), value: 5 },
].sort((a, b) => a.date - b.date);
const x = d3
  .scaleUtc()
  .domain(d3.extent(rows, (d) => d.date))
  .range([60, 600]);
const y = d3.scaleLinear().domain([0, 6]).range([280, 30]);
const line = d3
  .line()
  .defined((d) => d.value !== null && Number.isFinite(d.value))
  .x((d) => x(d.date))
  .y((d) => y(d.value));
const path = line(rows);
svg
  .append("path")
  .attr("d", path)
  .attr("fill", "none")
  .attr("stroke", "#2563eb")
  .attr("stroke-width", 3);
svg
  .append("g")
  .attr("transform", "translate(0,280)")
  .call(d3.axisBottom(x).ticks(d3.utcDay.every(1)).tickFormat(d3.utcFormat("%b %d")));
check(rows[0].date.toISOString() === "2024-01-01T00:00:00.000Z", "Dates not sorted");
check((path.match(/M/g) || []).length === 2, "Missing value did not split line");
""",
    "https://d3js.org/d3-scale/time",
    "https://d3js.org/d3-shape/line",
)

add(
    "Scatterplots, size encodings and overplotting",
    ["scatterplot", "area encoding", "overplotting", "correlation"],
    """A scatterplot uses two quantitative positions to show the joint distribution of observations. Each point should have a defined row grain, such as one person or one experiment. A visible association does not by itself establish causality, and a few synthetic points cannot support a population conclusion.

When a third quantity controls circle size, decide whether the quantity maps to radius or area. Viewers perceive the filled area, so a square-root radius scale often makes area proportional to a nonnegative quantity. Doubling a radius quadruples area. A legend should explain the size meaning.

Overplotting occurs when points overlap. Opacity, smaller marks, aggregation or a density representation can help, but each changes what the reader can infer. Jitter can reveal repeated values while deliberately moving positions; explain and bound it rather than presenting moved points as exact measurements.""",
    """Use independent x and y scales for their units. A `scaleSqrt` radius range maps nonnegative magnitude to radius. A circle at `(x(d.x), y(d.y))` encodes one record. Colors can represent categories, but labels or shapes should support readers who cannot distinguish the colors.

The reference validates finite positions and the area relationship for magnitudes 1 and 4. It does not perform a statistical test. Use a tooltip or table for exact records and make missing or invalid coordinates an explicit data policy.""",
    (
        "Compare radius and area",
        "The ratio follows the square of radius.",
        "const r=d3.scaleSqrt().domain([0,4]).range([0,20]);\nconsole.log(r(1),r(4));",
        "10 and 20; areas have ratio 1 to 4.",
    ),
    (
        "Detect duplicate coordinates",
        "Repeated positions can hide observations.",
        "const points=[{x:1,y:2},{x:1,y:2},{x:2,y:3}];\nconsole.log(new Set(points.map(d=>`${d.x},${d.y}`)).size);",
        "Two unique positions for three records.",
    ),
    [
        (
            "Predict circle radii for sizes 1 and 4.",
            "10 and 20 under the stated square-root scale.",
            "The radius ratio is two while the area ratio is four. This preserves the magnitude-to-area relation.",
        ),
        (
            "Add two identical coordinate records.",
            "The record count exceeds the unique visible position count.",
            "Overlap can conceal multiplicity. Record counts remain a data check even when marks visually coincide.",
        ),
        (
            "Build a three-variable scatterplot.",
            "Position and area mappings have named units and a size explanation.",
            "A chart should let a reader distinguish spatial coordinates from the meaning of marker area.",
        ),
        (
            "Diagnose mapping magnitude directly to radius.",
            "Area exaggerates large values quadratically.",
            "If area is the intended quantity encoding, use an appropriate radius transformation and validate a known ratio.",
        ),
        (
            "Choose a justified overplotting strategy.",
            "The strategy and its effect on interpretation are stated.",
            "Opacity, jitter and bins solve different tasks. Do not hide the transformation from readers.",
        ),
        (
            "Explain a correlation without claiming causation.",
            "Describe association and identify alternative explanations.",
            "Selection, confounding and reverse causality can create patterns. Visualization supports inquiry, not automatic causal identification.",
        ),
    ],
    r"""
const rows = [
  { id: "A", x: 1, y: 2, size: 1 },
  { id: "B", x: 2, y: 4, size: 4 },
  { id: "C", x: 3, y: 3, size: 2 },
];
const x = d3.scaleLinear().domain([0, 4]).range([60, 600]);
const y = d3.scaleLinear().domain([0, 5]).range([300, 30]);
const r = d3.scaleSqrt().domain([0, 4]).range([0, 24]);
svg
  .selectAll("circle")
  .data(rows, (d) => d.id)
  .join("circle")
  .attr("cx", (d) => x(d.x))
  .attr("cy", (d) => y(d.y))
  .attr("r", (d) => r(d.size))
  .attr("fill", "#7c3aed")
  .attr("fill-opacity", 0.65)
  .append("title")
  .text((d) => `${d.id}: x ${d.x}, y ${d.y}, size ${d.size}`);
svg.append("g").attr("transform", "translate(0,300)").call(d3.axisBottom(x));
svg.append("g").attr("transform", "translate(60,0)").call(d3.axisLeft(y));
check((r(4) * r(4)) / (r(1) * r(1)) === 4, "Area encoding wrong");
check(svg.selectAll("circle").size() === 3, "Record count wrong");
""",
    "https://d3js.org/d3-scale/pow",
    "https://d3js.org/d3-scale/ordinal",
)

add(
    "Histograms, bin boundaries and distribution shape",
    ["histogram", "threshold", "bin", "density"],
    """A histogram groups quantitative observations into intervals and displays their counts or density. The bins are numerical intervals, not arbitrary categories. Their boundaries affect the apparent distribution, especially with small samples. A meaningful histogram states the sample, units, domain and binning policy.

A bin usually includes its lower boundary and excludes its upper boundary, except the final bin includes its upper endpoint. This convention prevents double-counting values exactly on a threshold. Values outside the declared domain require a policy and should not disappear without explanation.

Count and density are different vertical quantities. With unequal bin widths, equal counts do not imply equal density. A density histogram uses height proportional to count divided by sample size and bin width, so area represents probability mass. The reference uses equal-width bins and counts to keep the first reasoning explicit.""",
    """`d3.bin().domain([0,10]).thresholds([2,4,6,8])` creates intervals with known edges. Each returned bin is an array of observations with x0 and x1 properties. The count is its length. A rectangle’s width follows x(x1)-x(x0), and its height follows the count scale.

Test boundary values explicitly. The sample `[0,2,2,4,9,10]` produces counts `[1,2,1,0,2]` for the chosen bins. The total count must equal the number of included finite observations. This simple conservation check catches many accidental exclusions.""",
    (
        "Inspect a threshold boundary",
        "The value 2 belongs to the interval starting at 2.",
        "const bins=d3.bin().domain([0,10]).thresholds([2,4,6,8])([0,2,2,4,9,10]);\nconsole.log(bins.map(b=>b.length));",
        "1, 2, 1, 0, 2.",
    ),
    (
        "Compute one density height",
        "This is an analytical quantity, not a plotting coordinate.",
        "const count=2, sampleSize=6, width=2;\nconsole.log(count/(sampleSize*width));",
        "1/6 per unit; the bin area is 1/3.",
    ),
    [
        (
            "Predict membership of value 2.",
            "It enters the bin whose lower edge is 2.",
            "The interval convention avoids counting one observation twice at a shared boundary.",
        ),
        (
            "Change thresholds while retaining the data.",
            "The shape changes while included total count remains six.",
            "Binning is a view of the same observations. A stable count invariant helps distinguish presentation choices from data loss.",
        ),
        (
            "Build the explicit-boundary count histogram.",
            "Five bins with counts 1,2,1,0,2.",
            "Use x0 and x1 for geometry rather than assuming all bin indices are data values.",
        ),
        (
            "Diagnose a missing maximum value.",
            "The final boundary convention or declared domain is wrong.",
            "A value equal to the final endpoint should be included under the stated D3 bin contract. Test it separately.",
        ),
        (
            "Explain unequal-width bin heights.",
            "Density is needed when area should represent probability mass.",
            "Raw counts with unequal widths can mislead visual comparisons. Normalize by width and sample size when using area semantics.",
        ),
        (
            "Compare two groups with different sample sizes.",
            "Choose counts or normalized density according to the comparison question.",
            "Counts show workload magnitude; density compares shapes. State which claim the chart supports.",
        ),
    ],
    r"""
const values = [0, 2, 2, 4, 9, 10];
const bins = d3.bin().domain([0, 10]).thresholds([2, 4, 6, 8])(values);
const x = d3.scaleLinear().domain([0, 10]).range([60, 600]);
const y = d3.scaleLinear().domain([0, 3]).range([300, 30]);
svg
  .selectAll("rect")
  .data(bins)
  .join("rect")
  .attr("x", (d) => x(d.x0) + 1)
  .attr("width", (d) => Math.max(0, x(d.x1) - x(d.x0) - 2))
  .attr("y", (d) => y(d.length))
  .attr("height", (d) => y(0) - y(d.length))
  .attr("fill", "#0f766e");
svg.append("g").attr("transform", "translate(0,300)").call(d3.axisBottom(x));
svg.append("g").attr("transform", "translate(60,0)").call(d3.axisLeft(y).ticks(3));
check(bins.map((b) => b.length).join(",") === "1,2,1,0,2", "Boundary counts wrong");
check(d3.sum(bins, (b) => b.length) === values.length, "Histogram lost data");
""",
    "https://d3js.org/d3-array/bin",
)

add(
    "Statistical summaries, box plots and uncertainty intervals",
    ["quantile", "median", "interval", "sampling uncertainty"],
    """A summary reduces a distribution to selected quantities. The median is a central order statistic; quartiles describe the middle part of the distribution. A box plot communicates chosen quantiles and whisker rules, which must be stated because conventions differ. It does not preserve every feature of the raw observations.

An uncertainty interval describes uncertainty about a parameter under a statistical procedure and assumptions. It is not the same as the spread of individual observations. A box showing sample quartiles and an interval around a mean answer different questions. Label both the statistic and the interval method when presenting estimates.

The lesson uses tiny synthetic samples to make quartiles and interval endpoints inspectable. It does not claim a confidence interval from an arbitrary pair of numbers. A visualization may render a supplied estimate and bounds correctly while the upstream statistical method is invalid; those checks remain separate.""",
    """Sort numerical values before using a function that assumes sorted input. `d3.quantileSorted` computes a quantile of an ordered array. For `[1,2,3,4,5]`, median is 3 and the first and third quartiles are 2 and 4. A simple box can map those values to x positions, with a median line inside.

For a supplied interval, check lower <= estimate <= upper before drawing a segment and point. If the interval spans zero, that visual fact should not be hidden by a truncated axis. The statistical interpretation still depends on the stated estimator and procedure.""",
    (
        "Compute transparent quartiles",
        "The input is explicitly sorted.",
        "const v=[1,2,3,4,5];\nconsole.log(d3.quantileSorted(v,0.25),d3.quantileSorted(v,0.5),d3.quantileSorted(v,0.75));",
        "2, 3 and 4.",
    ),
    (
        "Validate an interval before rendering",
        "This does not calculate the interval statistically.",
        "const estimate={value:0.2,lower:-0.1,upper:0.5};\nconsole.log(estimate.lower<=estimate.value && estimate.value<=estimate.upper);",
        "true; the supplied interval crosses zero.",
    ),
    [
        (
            "Predict the three quantiles.",
            "2,3,4 for the stated five-value sample.",
            "The small ordered input makes the definition visible. Different quantile conventions should be documented when comparing tools.",
        ),
        (
            "Add an extreme value and recompute.",
            "Quantiles and the visible range change according to the new sample.",
            "A summary is a function of data. Inspect how much information the box retains and which tail behavior it hides.",
        ),
        (
            "Draw a labeled box and median.",
            "The box endpoints map to Q1 and Q3 and the line maps to median.",
            "The geometry should encode actual statistics, not decorative percentages of chart width.",
        ),
        (
            "Diagnose calling an unsorted-only contract incorrectly.",
            "Sort a copy before quantileSorted.",
            "A function with a sorted-input precondition can return misleading values when that precondition is violated. The data pipeline owns the guarantee.",
        ),
        (
            "Distinguish individual spread from estimate uncertainty.",
            "Quartiles describe observations; a confidence interval concerns an estimator.",
            "They are not interchangeable error bars. Name the population quantity and method behind any inferential interval.",
        ),
        (
            "Design a comparison of two estimated effects.",
            "Show estimates, interval method, units and a meaningful zero reference.",
            "Visual overlap alone is not a complete hypothesis test. Explain the actual comparison procedure separately.",
        ),
    ],
    r"""
const values = [1, 2, 3, 4, 5];
const q1 = d3.quantileSorted(values, 0.25),
  median = d3.quantileSorted(values, 0.5),
  q3 = d3.quantileSorted(values, 0.75);
const x = d3.scaleLinear().domain([0, 6]).range([60, 600]);
svg
  .append("line")
  .attr("x1", x(1))
  .attr("x2", x(5))
  .attr("y1", 150)
  .attr("y2", 150)
  .attr("stroke", "#334155");
svg
  .append("rect")
  .attr("x", x(q1))
  .attr("y", 110)
  .attr("width", x(q3) - x(q1))
  .attr("height", 80)
  .attr("fill", "#c4b5fd")
  .attr("stroke", "#5b21b6");
svg
  .append("line")
  .attr("x1", x(median))
  .attr("x2", x(median))
  .attr("y1", 110)
  .attr("y2", 190)
  .attr("stroke", "#1e293b")
  .attr("stroke-width", 3);
svg.append("g").attr("transform", "translate(0,260)").call(d3.axisBottom(x));
svg
  .append("text")
  .attr("x", 60)
  .attr("y", 40)
  .text("Observed values: 1, 2, 3, 4, 5; whiskers show min/max");
check(q1 === 2 && median === 3 && q3 === 4, "Quantiles incorrect");
""",
    "https://d3js.org/d3-array/summarize",
)

add(
    "Grouped and stacked bars: totals, composition and denominators",
    ["stack", "grouped bars", "normalization", "denominator"],
    """Grouped bars support comparison of categories within several groups using a shared baseline for each bar. Stacked bars emphasize totals and composition, but interior segments do not share a common baseline. The choice depends on whether the reader needs precise subgroup comparisons or an overview of parts and whole.

A stack layout computes interval endpoints for each series in each row. The rectangle represents the distance between the lower and upper endpoints, not the upper endpoint alone. A normalized stack transforms each row to shares, which can hide differences in total magnitude.

A zero total has no meaningful fraction composition unless a policy is stated. Missing components also differ from known zeros. Preserve the original totals alongside a 100% chart so the reader can see whether a large-looking share represents two observations or two million.""",
    """`d3.stack().keys(['a','b'])` reads the named components from each record and returns one series for each key. A point is `[lower, upper]` and retains its original row in `.data`. Use y(lower)-y(upper) for positive vertical height.

`stackOffsetExpand` normalizes each row to unit total when appropriate. Validate finite nonnegative components for this introductory positive stack. Signed values need a different design, such as a diverging stack with explicit positive and negative baselines.""",
    (
        "Read stack endpoints",
        "The second component begins where the first ends.",
        'const series=d3.stack().keys(["a","b"])([{group:"X",a:2,b:3}]);\nconsole.log(series[0][0].slice(),series[1][0].slice());',
        "[0,2] and [2,5].",
    ),
    (
        "Compare counts and shares",
        "The same share can represent different totals.",
        "const rows=[{a:2,b:3},{a:20,b:30}];\nconsole.log(rows.map(d=>d.a/(d.a+d.b)));",
        "0.4 and 0.4 despite totals 5 and 50.",
    ),
    [
        (
            "Predict the stack endpoints.",
            "First segment0..2, second2..5.",
            "Endpoints are cumulative positions. The second segment height represents3, not5.",
        ),
        (
            "Normalize two proportional rows.",
            "Both have40% and60% shares despite different totals.",
            "Normalization removes absolute scale. Preserve totals if they matter to the analytical question.",
        ),
        (
            "Build a two-series stacked chart.",
            "Segment heights match component values and total heights match row sums.",
            "Check both component and total invariants. A plausible total can hide an incorrect internal segment calculation.",
        ),
        (
            "Diagnose using upper endpoint as segment height.",
            "Later segments are exaggerated because the lower endpoint was ignored.",
            "Compute the interval length in scale coordinates. Stack output is geometry input, not a direct height field.",
        ),
        (
            "Handle a zero-total group.",
            "Show an explicit no-composition state or documented zero representation.",
            "Dividing by zero does not produce an interpretable percentage. Do not invent shares to fill the chart.",
        ),
        (
            "Choose grouped or stacked bars for subgroup comparison.",
            "Use shared baselines when precise subgroup comparison is the primary task.",
            "A stack can still be useful for total composition, but the tradeoff should be explicit.",
        ),
    ],
    r"""
const rows = [
  { group: "X", a: 2, b: 3 },
  { group: "Y", a: 4, b: 2 },
];
const series = d3.stack().keys(["a", "b"])(rows);
const x = d3
  .scaleBand()
  .domain(rows.map((d) => d.group))
  .range([80, 580])
  .padding(0.3);
const y = d3.scaleLinear().domain([0, 7]).range([300, 30]);
svg
  .selectAll("g.series")
  .data(series)
  .join("g")
  .attr("class", "series")
  .attr("fill", (d, i) => ["#2563eb", "#f59e0b"][i])
  .selectAll("rect")
  .data((d) => d)
  .join("rect")
  .attr("x", (d) => x(d.data.group))
  .attr("y", (d) => y(d[1]))
  .attr("height", (d) => y(d[0]) - y(d[1]))
  .attr("width", x.bandwidth());
svg.append("g").attr("transform", "translate(0,300)").call(d3.axisBottom(x));
check(series[1][0][0] === 2 && series[1][0][1] === 5, "Stack endpoints wrong");
check(svg.selectAll("rect").size() === 4, "Segment count wrong");
""",
    "https://d3js.org/d3-shape/stack",
)

add(
    "Reusable and responsive chart components",
    ["component", "viewBox", "render contract", "empty state"],
    """A reusable chart component has an explicit input, output and lifecycle. It should not depend on a hidden global dataset or append another entire chart every time a caller updates it. A useful render contract specifies data shape, dimensions, identity, empty state and cleanup.

Responsive display is not the same as recomputing every data transformation on every resize. An SVG viewBox can scale an existing coordinate system to fit a container. More complex charts may need width-dependent tick density or label layout. Decide which parts change with available space and which analytical quantities remain invariant.

The reference renders into a caller-owned group and updates a keyed join. It checks that a second render does not duplicate marks and that an empty input produces a readable message. This is a foundation for dashboards whose views share state without sharing accidental DOM mutations.""",
    """Pass the container selection, data and size as arguments. Validate dimensions and records at the boundary. Compute scales from current input and update managed nodes. Keep the surrounding SVG and accessibility summary under clear ownership.

A ResizeObserver can detect actual container size, but it has a lifecycle and can trigger repeated callbacks. Disconnect it when the component is removed. The reference uses two explicit widths for deterministic acceptance; a real responsive integration should also be manually tested at narrow and wide browser sizes.""",
    (
        "Define a small render contract",
        "The function signature makes dependencies visible.",
        'function renderBars(group, rows, width){\n  if(!(width>0)) throw new Error("positive width required");\n  // Derive scales and reconcile only nodes owned by this component.\n}',
        "The caller supplies current rows and dimensions; the function does not fetch or use hidden app state.",
    ),
    (
        "Separate empty state from invalid geometry",
        "An empty dataset needs no min/max domain calculation.",
        'if(rows.length===0){\n  group.selectAll("rect").remove();\n  group.selectAll("text.empty").data([null]).join("text").attr("class","empty").text("No observations");\n}',
        "A visible no-data message replaces stale marks.",
    ),
    [
        (
            "Predict mark count after two renders.",
            "It equals current record count, not the sum of all prior counts.",
            "A component updates its owned nodes. Repeated calls should not accumulate entire charts.",
        ),
        (
            "Change width while retaining data.",
            "Geometry changes while values and identity remain stable.",
            "Responsive layout is a presentation transformation. It should not silently alter aggregation or records.",
        ),
        (
            "Implement a reusable bar renderer.",
            "Explicit inputs, keyed marks and a documented empty state.",
            "A small contract makes the component testable outside a large dashboard. Avoid hidden globals for data and dimensions.",
        ),
        (
            "Diagnose duplicate SVG trees after resize.",
            "The update path creates new roots rather than updating an owned tree.",
            "Choose a single owner for the SVG root and reconcile its children. Cleanup is part of component behavior.",
        ),
        (
            "Render an empty dataset after nonempty data.",
            "Stale marks disappear and the no-data message appears.",
            "Empty-state behavior must work on updates, not just initial load. Check both transitions.",
        ),
        (
            "Plan real narrow-screen acceptance.",
            "Readable labels, no clipping, keyboard access and stable data meaning.",
            "A scaled screenshot alone can conceal unreadable text. Inspect the actual interaction and label layout at the intended size.",
        ),
    ],
    r"""
const layer = svg.append("g");
function render(rows, width) {
  check(width > 0, "Width must be positive");
  const x = d3.scaleLinear().domain([0, 10]).range([0, width]);
  layer
    .selectAll("rect")
    .data(rows, (d) => d.id)
    .join("rect")
    .attr("x", 80)
    .attr("y", (d, i) => 50 + i * 70)
    .attr("width", (d) => x(d.value))
    .attr("height", 40)
    .attr("fill", "#0891b2");
  layer
    .selectAll("text.empty")
    .data(rows.length ? [] : [null])
    .join("text")
    .attr("class", "empty")
    .attr("x", 80)
    .attr("y", 100)
    .text("No observations");
}
render(
  [
    { id: "A", value: 3 },
    { id: "B", value: 6 },
  ],
  450,
);
render([{ id: "B", value: 6 }], 300);
check(layer.selectAll("rect").size() === 1, "Duplicate marks after update");
check(+layer.select("rect").attr("width") === 180, "Resize mapping wrong");
render([], 300);
check(
  layer.selectAll("rect").size() === 0 &&
    layer.select(".empty").text() === "No observations",
  "Empty state failed",
);
render(
  [
    { id: "A", value: 3 },
    { id: "B", value: 6 },
  ],
  450,
);
""",
    "https://d3js.org/d3-selection/joining",
    "https://developer.mozilla.org/en-US/docs/Web/API/ResizeObserver",
)

add(
    "Transitions, interruption and reduced-motion design",
    ["transition", "interpolation", "interruption", "reduced motion"],
    """A transition changes attributes over time rather than setting the final state immediately. Interpolation computes intermediate values, while easing controls the pace along the timeline. Motion can help a reader follow identity through a change, but it can also distract, delay access or imply a continuous process that the data does not represent.

Transitions are asynchronous. Starting one does not mean its final geometry exists on the next line. A newer update may interrupt an earlier transition, so a component must decide whether to finish, replace or cancel work. Awaiting a transition’s completion can reject when it is interrupted; handling that rejection is part of lifecycle correctness.

Reduced-motion preferences should lead to a useful static or immediate update. Do not make animation the only way to discover a value or state change. The reference uses a short bounded transition, respects the media preference and checks the final state after completion.""",
    """Name transitions when a component needs a clear interruption channel. Call `.interrupt(name)` before replacing obsolete work. A named transition’s `.end()` returns a promise for completion. The final data state should be stored independently of a partly animated attribute.

For deterministic testing, assert the final value after awaiting the promise, not after guessing a sleep duration. Timing varies across machines and background tabs. The reference does not run an infinite animation loop.""",
    (
        "Await the actual completion",
        "The mark is already selected.",
        'await mark.transition("update").duration(120).attr("cx",300).end();\nconsole.log(mark.attr("cx"));',
        "300 after successful completion, rather than an intermediate coordinate.",
    ),
    (
        "Respect reduced motion",
        "The data update still happens.",
        'const reduced=matchMedia("(prefers-reduced-motion: reduce)").matches;\nconst duration=reduced?0:120;',
        "The same final chart state with motion disabled when requested.",
    ),
    [
        (
            "Predict an attribute read immediately after starting a transition.",
            "It can still be the initial or intermediate value.",
            "Starting asynchronous work is not completion. Wait on the operation that defines the intended boundary.",
        ),
        (
            "Set duration to zero under reduced motion.",
            "The final value remains available without movement.",
            "Accessibility should preserve information and control, not remove the update entirely.",
        ),
        (
            "Implement a bounded transition with completion checks.",
            "Final geometry is asserted only after the transition ends.",
            "A guessed timeout can be flaky under load. Use the transition promise to synchronize with actual completion.",
        ),
        (
            "Diagnose a rejected end promise after a new update.",
            "The earlier transition may have been interrupted.",
            "Interruption is a meaningful lifecycle result. Handle it intentionally instead of treating every rejection as a successful animation.",
        ),
        (
            "Replace an obsolete transition by name.",
            "Only the component-owned update channel is interrupted.",
            "Named ownership avoids canceling unrelated animations. Keep data state separate from whatever intermediate geometry was visible.",
        ),
        (
            "Defend when to use a static update.",
            "Prefer immediate clarity when motion adds no explanatory value.",
            "Animation is a design choice, not a requirement of a polished chart. Respect speed, attention and motion sensitivity.",
        ),
    ],
    r"""
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
  .text(
    reduced
      ? "Immediate update: reduced motion requested"
      : "Bounded transition completed",
  );
""",
    "https://d3js.org/d3-transition/control-flow",
    "https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion",
)

add(
    "Pointer interaction, keyboard access and safe tooltips",
    ["event", "pointer coordinates", "tooltip", "keyboard focus"],
    """An interaction connects a user action to application state. D3 event handlers receive the event and the datum associated with the selected node. Pointer position is measured in a coordinate space; using page coordinates as SVG data values mixes two spaces and often produces misplaced tooltips or selections.

A tooltip is supplemental information, not the only place essential values should exist. A pointer-only tooltip excludes keyboard and some touch users. Provide focusable controls or an alternative data list, and keep a visible summary. Use text insertion so a data label containing markup characters remains text.

Native HTML buttons provide keyboard activation behavior. Making every SVG circle act like a button requires deliberate semantics, focus and key handling. For a small chart, a parallel list of native buttons can offer a simpler accessible route to selecting each datum.""",
    """`d3.pointer(event, node)` returns coordinates relative to the chosen node. A handler can update a selected ID and a text summary. Do not retain the event object as long-term application state; retain the meaningful data selection instead.

The reference draws circles and creates native buttons beneath the SVG. Both pointer and keyboard activation reach the same select function. It programmatically activates one button for a deterministic check, while the learner must still perform the real keyboard navigation.""",
    (
        "Insert a label as text",
        "This preserves literal characters rather than parsing markup.",
        'd3.select(host).append("p").text("<strong>sample</strong>");',
        "The angle-bracket text appears literally; no strong element is created.",
    ),
    (
        "Share one action between input methods",
        "A native button handles keyboard activation.",
        'button.addEventListener("click",()=>selectRow(row));\nmark.on("pointerenter",()=>selectRow(row));',
        "Both paths update the same selected record and summary.",
    ),
    [
        (
            "Predict literal markup in a text label.",
            "It remains text instead of becoming executable HTML.",
            "Text insertion is the appropriate default for data labels. Do not use HTML parsing merely to make labels easier to style.",
        ),
        (
            "Activate the same record by pointer and keyboard.",
            "Both produce the same selection summary.",
            "Input methods should converge on application state, not implement subtly different data transformations.",
        ),
        (
            "Build an accessible selection list beside the chart.",
            "Native buttons are reachable and reveal exact record values.",
            "A chart can have a rich visual layer while retaining a simple semantic interaction route.",
        ),
        (
            "Diagnose a tooltip offset after SVG scaling.",
            "Coordinates were measured in the wrong space.",
            "Choose the target coordinate system and use the corresponding conversion. Arbitrary pixel offsets hide the mismatch only at one size.",
        ),
        (
            "Keep essential values available without hover.",
            "A summary or data list remains visible and usable.",
            "Hover is not universal. Touch, keyboard and assistive-technology users need a reliable route to the same information.",
        ),
        (
            "Review focus and announcement behavior.",
            "Focus stays predictable and the live summary is concise.",
            "Avoid moving focus on every hover or announcing a large changing DOM. Test the actual keyboard sequence rather than assuming ARIA alone implements it.",
        ),
    ],
    r"""
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
""",
    "https://d3js.org/d3-selection/events",
    "https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles/status_role",
)

add(
    "Brushing and coordinated views",
    ["brush", "selection range", "linked view", "state"],
    """A brush lets a user choose a spatial interval or rectangle. The brush selection is expressed in display coordinates. The analytical selection is usually expressed in data values or record IDs. Convert between those spaces explicitly and decide which boundary values count as selected.

Linked views share application state: selecting a range in one chart changes the records or emphasis in another. If each chart keeps an unrelated hidden selection, the dashboard can contradict itself. A small state object and a pure filter function make coordination easier to inspect.

A drag gesture is not an accessible interface by itself. Provide a reset and a keyboard-friendly way to choose a meaningful preset or numeric interval. Show the selected range and count as text so the effect is understandable without interpreting color alone.""",
    """`d3.brushX()` defines a horizontal brush with an explicit extent. Its event selection is null when cleared, otherwise a pair of pixel coordinates. Use `x.invert` to recover data values. Handle null as an intentional full or empty selection according to the documented policy.

The reference uses inclusive data bounds and a preset range from 2 to 4. It calls the same brush move path used by interaction, then asserts selected IDs. Programmatic movement proves state wiring; manual pointer and keyboard checks remain separate.""",
    (
        "Convert brush pixels to values",
        "A known scale makes the conversion testable.",
        "const x=d3.scaleLinear().domain([0,10]).range([50,550]);\nconsole.log([x.invert(150),x.invert(250)]);",
        "[2,4].",
    ),
    (
        "Handle clearing explicitly",
        "The policy here treats a cleared brush as all records.",
        "function selected(rows,range){return range===null?rows:rows.filter(d=>d.x>=range[0]&&d.x<=range[1]);}",
        "Clearing restores the full record set rather than reusing stale bounds.",
    ),
    [
        (
            "Predict the selected values for range2..4.",
            "Values2,3,4 under inclusive bounds.",
            "Boundary policy is part of the analytical contract. Test exact endpoints instead of relying on visual proximity.",
        ),
        (
            "Clear the brush.",
            "The full dataset returns under the stated policy.",
            "Null is an intentional state, not an error to ignore. Stale filters are a common linked-view bug.",
        ),
        (
            "Link a brush to a textual record list.",
            "The list and visual selection describe the same IDs.",
            "Both views should derive from one selection state so they cannot drift independently.",
        ),
        (
            "Diagnose filtering with raw pixels against data values.",
            "The coordinate spaces were mixed.",
            "Invert through the same scale that positioned the marks. Changing chart size then remains meaningful.",
        ),
        (
            "Add a keyboard-accessible preset and reset.",
            "Native controls reach the same state update as brushing.",
            "The alternative should preserve the actual analytical action, not merely display a decorative button.",
        ),
        (
            "Design a two-chart coordination rule.",
            "One shared selected-ID set drives both views.",
            "Keep data filtering and rendering separate. This makes interactions testable without depending on exact pixel appearance.",
        ),
    ],
    r"""
const rows = d3.range(1, 6).map((x) => ({ id: String(x), x }));
const x = d3.scaleLinear().domain([0, 6]).range([50, 590]);
const marks = svg
  .selectAll("circle")
  .data(rows)
  .join("circle")
  .attr("cx", (d) => x(d.x))
  .attr("cy", 150)
  .attr("r", 16);
const status = d3.select(host).append("p").attr("role", "status");
let selected = [];
const brush = d3
  .brushX()
  .extent([
    [50, 80],
    [590, 220],
  ])
  .on("brush end", (event) => {
    const range = event.selection?.map(x.invert);
    selected = range
      ? rows.filter((d) => d.x >= range[0] - 1e-9 && d.x <= range[1] + 1e-9)
      : rows;
    const ids = new Set(selected.map((d) => d.id));
    marks.attr("fill", (d) => (ids.has(d.id) ? "#2563eb" : "#cbd5e1"));
    status.text(`Selected: ${selected.map((d) => d.id).join(", ")}`);
  });
const layer = svg.append("g").call(brush);
d3.select(host)
  .append("button")
  .attr("type", "button")
  .text("Select 2 through 4")
  .on("click", () => layer.call(brush.move, [x(2), x(4)]));
d3.select(host)
  .append("button")
  .attr("type", "button")
  .text("Reset selection")
  .on("click", () => layer.call(brush.move, null));
layer.call(brush.move, [x(2), x(4)]);
check(selected.map((d) => d.id).join(",") === "2,3,4", "Brush data conversion wrong");
""",
    "https://d3js.org/d3-brush",
)

add(
    "Zoom, pan and rescaled axes",
    ["zoom transform", "rescaleX", "viewport", "reset"],
    """Zoom changes the mapping between data space and the visible viewport. A transform typically contains a scale factor and translation. Panning changes which portion of the data is visible; it does not change the underlying observations. Keep the original scale and data separate from the transformed view.

Simply scaling an SVG group can also enlarge text and marker sizes, which may or may not be intended. Rescaling an axis from the zoom transform can preserve readable labels while changing the displayed data domain. Clipping keeps marks within the intended plot region.

A usable zoom interface needs bounds and a reset. Pointer gestures can conflict with page scrolling, so test the actual browser behavior. Keyboard controls or preset views provide an alternative to wheel and drag gestures. Never use zoom to conceal a misleading initial domain.""",
    """`event.transform.rescaleX(baseScale)` creates a scale for the transformed horizontal view. Use that same scale for marks and axis ticks. The base scale remains unchanged so reset has a stable reference.

Set explicit extent and scaleExtent for predictable behavior. The reference applies a known transform programmatically, checks the visible domain narrows and then resets. This establishes the transformation logic; manual interaction acceptance still includes pointer and keyboard behavior.""",
    (
        "Inspect a known transform",
        "A transform modifies visual coordinates.",
        "const t=d3.zoomIdentity.translate(-100,0).scale(2);\nconsole.log(t.applyX(100));",
        "100 because scale and translation combine as2*100-100.",
    ),
    (
        "Derive an axis from the view",
        "The original scale remains available for reset.",
        "const view=transform.rescaleX(base);\naxis.call(d3.axisBottom(view));",
        "Ticks represent the transformed data domain rather than the unchanged original domain.",
    ),
    [
        (
            "Predict transformed coordinate100.",
            "100 under translation-100 and scale2.",
            "Transform order is encoded by the D3 transform representation. Test a known value before applying it to all marks.",
        ),
        (
            "Compare original and zoomed domains.",
            "The view domain narrows while the base domain stays unchanged.",
            "Zoom is a view state. Mutating the base repeatedly can accumulate errors and make reset unreliable.",
        ),
        (
            "Implement linked mark and axis zooming.",
            "Both use the same rescaled view.",
            "A moving chart with a stale axis gives false numeric meaning. Treat axis updates as part of the interaction contract.",
        ),
        (
            "Diagnose enlarged labels after scaling the whole group.",
            "Geometry and text were transformed together.",
            "Decide which visual properties should stay constant. Rescale positions and redraw axes when readable text is the goal.",
        ),
        (
            "Add a native reset button.",
            "The initial domain and mark positions are restored.",
            "Reset should use the stable base transform, not infer an inverse from partially mutated state.",
        ),
        (
            "Review zoom for a long time series.",
            "Bounds, clipping, readable ticks and accessible alternate controls.",
            "Navigation should help analysis without trapping scrolling or hiding context. Keep an overview or clear current-domain label when needed.",
        ),
    ],
    r"""
const rows = d3.range(11).map((x) => ({ x, y: Math.sin(x) }));
const base = d3.scaleLinear().domain([0, 10]).range([60, 590]);
const y = d3.scaleLinear().domain([-1, 1]).range([270, 40]);
const axis = svg.append("g").attr("transform", "translate(0,300)");
const marks = svg
  .selectAll("circle")
  .data(rows)
  .join("circle")
  .attr("cy", (d) => y(d.y))
  .attr("r", 5)
  .attr("fill", "#0f766e");
let view = base;
const zoom = d3
  .zoom()
  .extent([
    [60, 30],
    [590, 300],
  ])
  .scaleExtent([1, 4])
  .on("zoom", (event) => {
    view = event.transform.rescaleX(base);
    marks.attr("cx", (d) => view(d.x));
    axis.call(d3.axisBottom(view));
  });
svg.call(zoom);
d3.select(host)
  .append("button")
  .attr("type", "button")
  .text("Reset zoom")
  .on("click", () => svg.call(zoom.transform, d3.zoomIdentity));
svg.call(zoom.transform, d3.zoomIdentity.translate(-60, 0).scale(2));
check(view.domain()[1] - view.domain()[0] < 10, "Zoom domain did not narrow");
check(base.domain().join(",") === "0,10", "Base scale mutated");
svg.call(zoom.transform, d3.zoomIdentity);
check(view.domain().join(",") === "0,10", "Reset failed");
""",
    "https://d3js.org/d3-zoom",
)

add(
    "Hierarchies and tree layouts",
    ["hierarchy", "parent", "tree layout", "link"],
    """A hierarchy represents parent-child relationships without cycles. A tree has one root and a unique path from that root to each node. This differs from a general network, where nodes can have several relationships and cycles. Choosing a tree layout for data that is not a tree can hide important structure.

`d3.hierarchy` wraps nested input in nodes with parent, children, depth and traversal methods. Layout algorithms add geometry to these wrapper nodes. The original data remains available as node.data. A tree layout uses topology, not a numeric magnitude, to position nodes.

The reference visualizes a small learning taxonomy. Labels explain the nodes, and links show parent-child relationships. A hierarchy can be deep or broad, so a reusable view must address label collisions, collapse state and keyboard navigation rather than assuming every tree fits one screen.""",
    """Construct the hierarchy from an object whose children field contains nested objects. Apply `d3.tree().size([height,width])` to compute coordinates. For a left-to-right tree, use the layout y coordinate as horizontal position and x as vertical position.

`root.links()` returns source-target pairs; `d3.linkHorizontal` converts each pair into a path. Check node and edge counts: a connected tree with n nodes has n-1 parent edges. This is a structural invariant, not a visual preference.""",
    (
        "Count a tiny hierarchy",
        "The wrapper exposes descendants and links.",
        'const root=d3.hierarchy({name:"Root",children:[{name:"A"},{name:"B"}]});\nconsole.log(root.descendants().length,root.links().length);',
        "3 nodes and2 parent links.",
    ),
    (
        "Distinguish topology from magnitude",
        "A tree layout does not require a size value.",
        "d3.tree().size([250,450])(root);\nconsole.log(root.children.every(d=>d.depth===1));",
        "true; depth is a structural property.",
    ),
    [
        (
            "Predict node and edge counts.",
            "Three nodes and two links in the small example.",
            "Each non-root node has one parent edge. This invariant catches missing or duplicated structural relationships.",
        ),
        (
            "Add a grandchild under A.",
            "Depth2 appears and counts become4 nodes,3 links.",
            "The new relationship changes topology. Its position should follow the layout rather than a manually chosen unrelated coordinate.",
        ),
        (
            "Render a labeled left-to-right tree.",
            "Links connect the matching source and target nodes.",
            "Use the same layout coordinates for both marks and links. Swapping x and y inconsistently produces misleading connections.",
        ),
        (
            "Diagnose using a tree for a cyclic relationship graph.",
            "The data model does not satisfy tree assumptions.",
            "A general network needs a different representation or an explicitly chosen spanning tree whose omissions are disclosed.",
        ),
        (
            "Handle long labels in a narrow view.",
            "Labels remain readable or an alternate list exposes full names.",
            "Truncation needs a discoverable full value. Geometric fit alone does not establish usable reading.",
        ),
        (
            "Design a collapsible taxonomy state model.",
            "Stable node IDs and explicit collapsed sets preserve identity.",
            "Do not encode collapse only by deleting data permanently. Keep the source hierarchy and view state distinct.",
        ),
    ],
    r"""
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
check(
  root.descendants().length === 6 && root.links().length === 5,
  "Tree structure incorrect",
);
check(
  root.descendants().every((d) => Number.isFinite(d.x) && Number.isFinite(d.y)),
  "Nonfinite layout",
);
""",
    "https://d3js.org/d3-hierarchy/hierarchy",
    "https://d3js.org/d3-hierarchy/tree",
)

add(
    "Treemaps and area-based composition",
    ["treemap", "hierarchical sum", "area", "tiling"],
    """A treemap divides a rectangular area into nested regions whose areas represent nonnegative values. It is useful for part-to-whole structure when many categories must fit in a compact view. Exact comparisons are harder than aligned position or length, so a table or labels should support precise reading.

Hierarchy sums need a clear grain. If a parent value already includes its children and you also sum the children, the total can be double-counted. A common input supplies values only at leaves and uses hierarchy.sum to aggregate upward. Missing or negative values require an explicit policy.

Padding and rounding change visible rectangle area, so pixel area may not exactly preserve ratios in tiny charts. This is a rendering tradeoff, not a reason to claim numerical precision from a treemap. The reference checks the hierarchy’s numeric total and nonnegative geometry separately.""",
    """Create the hierarchy, call `.sum(d => d.value || 0)` only under a validated nonnegative-value contract, then apply a treemap layout. Each leaf receives x0,y0,x1,y1 bounds. Width is x1-x0 and height is y1-y0.

Sort deliberately if stable ordering matters. Updating values can substantially rearrange a treemap, making entity tracking difficult. Use stable keys and consider whether a bar chart would better serve the comparison task.""",
    (
        "Aggregate leaf values",
        "Parents have no independent duplicated amount.",
        'const root=d3.hierarchy({children:[{name:"A",value:2},{name:"B",value:3}]}).sum(d=>d.value||0);\nconsole.log(root.value);',
        "5.",
    ),
    (
        "Read rectangle geometry",
        "Bounds are positions, not direct widths.",
        "const leaf={x0:10,x1:110,y0:20,y1:70};\nconsole.log(leaf.x1-leaf.x0,leaf.y1-leaf.y0);",
        "Width100 and height50.",
    ),
    [
        (
            "Predict the hierarchy total.",
            "5 from leaf values2 and3.",
            "The aggregate should match the known leaf sum. Adding a duplicated parent amount would overstate the total.",
        ),
        (
            "Add a zero-valued leaf.",
            "The numeric total stays unchanged and its representation needs an explicit policy.",
            "Zero area can make a category invisible. Preserve its name in a table or explanation if it belongs to the analytical universe.",
        ),
        (
            "Render labeled leaf rectangles.",
            "Bounds are finite and widths/heights are nonnegative.",
            "Validate geometry separately from numeric sums. Padding can alter visible area without changing the underlying values.",
        ),
        (
            "Diagnose parent-plus-child double counting.",
            "The input mixes aggregate and leaf grain.",
            "Choose one source of truth for the sum. A layout cannot infer that one value already includes another.",
        ),
        (
            "Compare treemap and bars for precise ranking.",
            "Bars usually offer easier aligned magnitude comparison.",
            "Treemaps prioritize compact hierarchy and composition. State the task that justifies the area encoding.",
        ),
        (
            "Design a changing treemap with identity preserved.",
            "Stable keys, explicit updates and a readable alternate value list.",
            "Large layout changes can disorient viewers. Identity and textual values help them follow the same entity across updates.",
        ),
    ],
    r"""
const root = d3
  .hierarchy({
    name: "Total",
    children: [
      { name: "Analysis", value: 6 },
      { name: "Engineering", value: 3 },
      { name: "Design", value: 1 },
    ],
  })
  .sum((d) => d.value || 0);
d3.treemap().size([540, 260]).padding(3)(root);
const cells = svg
  .append("g")
  .attr("transform", "translate(50,40)")
  .selectAll("g")
  .data(root.leaves(), (d) => d.data.name)
  .join("g")
  .attr("transform", (d) => `translate(${d.x0},${d.y0})`);
cells
  .append("rect")
  .attr("width", (d) => d.x1 - d.x0)
  .attr("height", (d) => d.y1 - d.y0)
  .attr("fill", (d, i) => ["#bfdbfe", "#c4b5fd", "#99f6e4"][i]);
cells
  .append("text")
  .attr("x", 8)
  .attr("y", 24)
  .text((d) => `${d.data.name}: ${d.value}`);
check(root.value === 10, "Hierarchy sum incorrect");
check(
  root.leaves().every((d) => d.x1 >= d.x0 && d.y1 >= d.y0),
  "Invalid treemap geometry",
);
""",
    "https://d3js.org/d3-hierarchy/treemap",
)

add(
    "Networks, force simulation and reproducible layouts",
    ["graph", "force simulation", "mutation", "layout convergence"],
    """A network or graph contains nodes and edges. Unlike a tree, it can contain cycles and multiple routes. A force-directed layout assigns positions by iteratively applying simulated forces such as attraction along links and repulsion between nodes. The result is a layout heuristic, not evidence that geometric distance is a measured relationship strength.

D3 force simulation mutates node objects with position and velocity fields and can replace link endpoint IDs with node references. Copy input records before giving them to a simulation if another component owns immutable source data. Stable node IDs define link identity.

An automatically running simulation has a timer and a lifecycle. For a small deterministic lesson, stop it and advance a fixed number of ticks with a seeded random source. This makes checks repeatable and prevents a background timer from continuing after the lesson result is recorded.""",
    """Create node and link copies, configure `forceLink(...).id(d=>d.id)`, charge and centering forces, and call `.stop()` before manual ticks. Each tick updates the layout. A finite position check verifies basic numerical health but does not prove the chosen force parameters produce a useful explanation.

Render links from their resolved source and target nodes and render labeled circles for nodes. A larger graph needs aggregation, filtering, interaction and performance planning. Do not call a dense hairball an informative visualization merely because every edge is drawn.""",
    (
        "Preserve source ownership",
        "The simulation receives its own mutable copies.",
        "const nodes=sourceNodes.map(d=>({...d}));\nconst links=sourceLinks.map(d=>({...d}));",
        "Layout mutation does not add x/y fields to the original source objects.",
    ),
    (
        "Bound simulation work",
        "A fixed tick count replaces an unbounded animation loop.",
        "const simulation=d3.forceSimulation(nodes).randomSource(d3.randomLcg(0.5)).stop();\nsimulation.tick(80);",
        "The simulation advances80 steps and has no running timer afterward.",
    ),
    [
        (
            "Distinguish graph relationships from layout distance.",
            "Edges are data; force positions are a chosen visual arrangement.",
            "A short geometric distance can be an artifact of parameters rather than a measured similarity.",
        ),
        (
            "Copy node and link objects before simulation.",
            "Original inputs remain free of layout mutation.",
            "This protects shared application state. Shallow copies are sufficient only when the mutable fields are at the copied level.",
        ),
        (
            "Build a bounded three-node network.",
            "All positions are finite and every link resolves to known IDs.",
            "Validate topology before layout. An unknown endpoint should fail clearly rather than create an unexplained missing edge.",
        ),
        (
            "Diagnose a reference that never stops animating.",
            "The simulation timer lacks a lifecycle boundary.",
            "Stop or dispose of owned work. A completed lesson receipt should not leave unnecessary background computation.",
        ),
        (
            "Test duplicate or unknown node IDs.",
            "The input is rejected before misleading layout.",
            "Identity validation prevents ambiguous link resolution. A visually plausible graph can still represent the wrong entities.",
        ),
        (
            "Choose a strategy for a dense network.",
            "Filter or aggregate according to an analytical question.",
            "Drawing every possible edge can obscure structure. Explain the retained relationships and any information omitted.",
        ),
    ],
    r"""
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
""",
    "https://d3js.org/d3-force/simulation",
    "https://d3js.org/d3-force/link",
)

add(
    "Geographic data, GeoJSON and projection choices",
    ["GeoJSON", "longitude", "projection", "geoPath"],
    """GeoJSON represents geographic features using geometry and properties. Geographic coordinates conventionally use longitude then latitude in degrees. Swapping them can produce plausible but incorrect locations. A map projection converts positions on the globe into a flat display, introducing distortion because a sphere cannot be flattened without tradeoffs.

Different projections preserve different properties locally or globally. A map for comparing area should not casually use a projection that strongly distorts area. A map for route direction has another purpose. State the geographic scope and the projection’s relevance to the analytical question.

The reference uses a tiny original synthetic point collection, so it needs no external map download or geographic dataset license. It demonstrates coordinate conversion and path creation without pretending that dots alone are a detailed basemap. Real geographic boundaries also require source, date and topology review.""",
    """A FeatureCollection contains Feature objects with geometry and properties. `d3.geoMercator` returns a projection callable on `[longitude,latitude]`. `d3.geoPath(projection)` converts GeoJSON into SVG path data. Fitting a projection to data chooses scale and translation for a view, not an analytical normalization of values.

Check that all projected coordinates are finite and within the intended view. A coordinate can be valid globally yet outside your chosen region. Handle antimeridian crossings and polygon winding deliberately for actual region datasets; those cases are not solved by swapping arbitrary signs until a map looks right.""",
    (
        "Respect coordinate order",
        "Longitude is first.",
        'const point={type:"Point",coordinates:[10,45]};\nconsole.log(point.coordinates[0]);',
        "10 degrees longitude, not latitude.",
    ),
    (
        "Project the origin",
        "A known center provides a useful anchor.",
        "const projection=d3.geoMercator().center([0,0]).scale(100).translate([320,180]);\nconsole.log(projection([0,0]));",
        "Approximately[320,180].",
    ),
    [
        (
            "Identify longitude and latitude positions.",
            "The first coordinate is longitude and the second latitude.",
            "GeoJSON order is part of the data contract. A swapped pair can still fall within numeric bounds and silently map the wrong place.",
        ),
        (
            "Change a longitude while holding latitude fixed.",
            "The projected horizontal location changes under this projection.",
            "Use a known anchor to reason about direction before interpreting an unfamiliar region.",
        ),
        (
            "Render the synthetic point collection.",
            "One finite path per feature with descriptive labels.",
            "Keep feature identity and geometry separate from visual styling. No external fetch is required.",
        ),
        (
            "Diagnose a misplaced but numerically valid point.",
            "Check coordinate order, units, projection and source reference system.",
            "Visual plausibility is not enough. Use known landmarks or synthetic anchors to localize the mismatch.",
        ),
        (
            "Explain projection distortion.",
            "A flat map cannot preserve every geographic property simultaneously.",
            "Choose the property relevant to the task and state the tradeoff. A familiar projection is not automatically appropriate for area comparison.",
        ),
        (
            "Plan a real boundary-data integration.",
            "Source/license, date, stable IDs, topology and projection checks.",
            "The map must be reproducible and legally distributable. Offline packaging needs deliberate acquisition and attribution, not a hidden runtime download.",
        ),
    ],
    r"""
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
svg
  .selectAll("path")
  .data(data.features)
  .join("path")
  .attr("d", path)
  .attr("fill", "#2563eb");
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
""",
    "https://d3js.org/d3-geo/projection",
    "https://datatracker.ietf.org/doc/html/rfc7946",
)

add(
    "Choropleths, rate denominators and missing geographic joins",
    ["choropleth", "rate", "geographic join", "missing data"],
    """A choropleth colors geographic regions according to a value. The map’s geometry and the statistical table usually come from different sources, so they must be joined by a stable identifier. A display name is often a weak key because spelling, language and boundary definitions can change.

Raw counts often track population or exposure rather than the phenomenon of interest. A rate divides an event count by a relevant denominator, such as eligible people or observation time. The denominator must match the numerator’s geography, period and population. A beautiful map cannot repair a mismatched denominator.

Missing data needs its own visual state. A region with no measurement is not equivalent to a measured zero. Keep an explicit missing color or pattern, a legend and a table. Be cautious about ecological inference: a region-level association does not necessarily describe individuals within that region.""",
    """Create a Map from stable region ID to validated data, then look up each feature’s ID. Validate duplicate statistical IDs and report unmatched features and rows. Compute rates only for positive valid denominators. Choose a sequential scale for nonnegative ordered rates and explain its domain.

The reference uses synthetic planar regions with `geoIdentity`, so the lesson isolates join and rate logic without introducing a global projection. It includes one missing region deliberately. This is a map-like teaching fixture, not a real-world geographic claim.""",
    (
        "Compute an explicit rate",
        "Numerator and denominator have the same scope.",
        "const rate=(events,population)=>population>0?events/population:null;\nconsole.log(rate(10,100),rate(10,0));",
        "0.1 and null; zero denominator is not a valid rate.",
    ),
    (
        "Distinguish missing and zero",
        "Map membership is separate from a numeric value.",
        'const values=new Map([["A",0]]);\nconsole.log(values.has("A"),values.has("B"));',
        "A is measured zero; B has no supplied record.",
    ),
    [
        (
            "Predict rates for10/100 and20/100.",
            "0.1 and0.2 with an explicit common denominator meaning.",
            "A rate is a derived quantity. Preserve numerator and denominator so the calculation can be audited.",
        ),
        (
            "Add a region with no statistical row.",
            "It receives the documented missing-data appearance.",
            "Do not default a failed join to zero. Missingness is an observation about data availability.",
        ),
        (
            "Build a stable-ID choropleth join.",
            "Every feature is matched or explicitly listed as missing.",
            "A join audit prevents silent region loss and name-based mismatches. Keep unmatched statistical rows visible too.",
        ),
        (
            "Diagnose a map of raw events interpreted as risk.",
            "Population or exposure may explain the count pattern.",
            "Choose a denominator appropriate to the question and verify its geographic and temporal alignment.",
        ),
        (
            "Handle a zero denominator.",
            "Reject or mark the rate undefined rather than divide to infinity.",
            "An invalid denominator cannot support a meaningful color. The chart should expose the limitation.",
        ),
        (
            "Explain ecological inference limits.",
            "Regional summaries do not automatically describe individuals.",
            "Aggregation can create or reverse relationships. State the unit of analysis and avoid unsupported individual conclusions.",
        ),
    ],
    r"""
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
""",
    "https://d3js.org/d3-scale/sequential",
    "https://d3js.org/d3-geo/path",
)

add(
    "Canvas, rendering cost and spatial hit testing",
    ["Canvas", "device pixel ratio", "hit testing", "quadtree"],
    """SVG keeps a DOM node for each mark, making styling and interaction convenient. Canvas draws pixels into one bitmap, which can reduce DOM overhead for many simple marks. Canvas does not automatically provide a separate accessible or interactive element for each point. The author must supply semantics and hit testing.

A Canvas has a backing resolution and a CSS display size. Device pixel ratio can make a one-to-one backing bitmap look blurry on high-density screens. Scale the backing dimensions and drawing context deliberately while keeping analytical coordinates in the documented logical space.

Performance depends on data size, transformations, layout, rendering and interactions. Switching to Canvas does not fix an expensive quadratic data algorithm. Measure the slow stage, avoid repeated allocations where appropriate and preserve an accessible data summary or table.""",
    """Set canvas.width and height for the backing bitmap, set CSS width and height for display, then transform the context by the device pixel ratio. Draw circles with beginPath, arc and fill. A quadtree can search nearby points efficiently, but its coordinates must match the pointer coordinate space.

The reference draws a bounded grid of100 points and performs a known nearest-point lookup. It does not benchmark a million records or claim universal Canvas superiority. The SVG is hidden for this lesson because the output is the Canvas plus a textual summary.""",
    (
        "Separate display and backing dimensions",
        "Logical size remains320 by180.",
        'const ratio=Math.min(devicePixelRatio||1,2);\ncanvas.width=320*ratio; canvas.height=180*ratio;\ncanvas.style.width="320px"; canvas.style.height="180px";\ncontext.setTransform(ratio,0,0,ratio,0,0);',
        "Drawing coordinates stay logical while the backing bitmap gains resolution.",
    ),
    (
        "Find a nearby point",
        "The query is in the same coordinate system as the data.",
        'const tree=d3.quadtree().x(d=>d.x).y(d=>d.y).addAll([{id:"A",x:10,y:10},{id:"B",x:90,y:90}]);\nconsole.log(tree.find(12,11).id);',
        "A.",
    ),
    [
        (
            "Predict DOM mark count for a Canvas plot.",
            "One Canvas can draw many points without one DOM node per point.",
            "The reduced DOM cost comes with extra responsibility for interaction and semantics.",
        ),
        (
            "Change device pixel ratio while retaining logical positions.",
            "The plot geometry stays the same size while bitmap resolution changes.",
            "Do not apply the ratio twice to pointer coordinates or mark positions.",
        ),
        (
            "Draw100 bounded points and a textual summary.",
            "The Canvas is visible and the count is available as text.",
            "A bitmap alone is not an accessible data representation. Provide the information needed for the analytical task outside pixels.",
        ),
        (
            "Diagnose a hit test that selects the wrong point after scaling.",
            "Pointer and indexed coordinates use different spaces.",
            "Convert once into the logical coordinate system and query the index there. Random offsets are not a stable repair.",
        ),
        (
            "Compare transformation and rendering costs.",
            "Measure the actual slow stage before replacing the renderer.",
            "Canvas can reduce mark rendering overhead while leaving aggregation or layout cost unchanged.",
        ),
        (
            "Design an accessible large-scatter interface.",
            "Canvas marks plus keyboard filtering, summary and exact-record access.",
            "Performance and accessibility are joint requirements. A faster unreadable bitmap is not a complete product improvement.",
        ),
    ],
    r"""
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
""",
    "https://d3js.org/d3-quadtree",
    "https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API",
)

add(
    "Dashboard state, cross-filtering and reproducible views",
    ["state", "derived data", "cross-filter", "single source of truth"],
    """A dashboard coordinates multiple views around shared analytical state. Filters, selected IDs and display options belong in an explicit model. Each chart should derive its visible records from that model rather than mutating another chart’s DOM as an informal message bus.

Cross-filtering can change denominators. If a category chart selects one group, a rate chart must state whether its denominator is the filtered group or the full population. A dashboard can be internally consistent in code while making a misleading comparison because the analytical universe changed silently.

Pure transformation functions are easier to test than event-heavy code. A filter function takes rows and state and returns a derived result without editing the source. Rendering then consumes that result. This separation helps preserve reproducibility, reset behavior and a clear explanation of what the current view means.""",
    """Use one `state` object and an `update(nextState)` function that derives data and renders every view. Native controls dispatch state changes. Keep the original rows immutable by convention or freeze them in a small example. A reset restores a known initial state.

The reference links a category filter to bars and a numeric summary. Programmatic control activation checks state wiring, while manual keyboard review checks the actual user experience. Saving a dashboard view should record filter values and data identity, not only a screenshot.""",
    (
        "Derive data without mutation",
        "The filter is a pure computation.",
        'const derive=(rows,state)=>rows.filter(d=>state.group==="all"||d.group===state.group);',
        "Source rows remain unchanged; the output reflects the current group choice.",
    ),
    (
        "Make denominator explicit",
        "Two summaries answer different questions.",
        "const selectedRate=selectedEvents/selectedEligible;\nconst populationShare=selectedEvents/allEvents;",
        "A within-group rate differs from a share of all events.",
    ),
    [
        (
            "Predict selected IDs for groupA.",
            "Only records whose group isA remain.",
            "A filter is a precise predicate. Check IDs before trusting a changed chart.",
        ),
        (
            "Reset the dashboard to all groups.",
            "Every view returns to the same initial analytical universe.",
            "Reset must update shared state and all derived views, not merely clear one control’s visual highlight.",
        ),
        (
            "Build two coordinated views from one state.",
            "Bars and summary report the same selected records and total.",
            "Derive once or use the same pure predicate. Independent hidden filters can create contradictory outputs.",
        ),
        (
            "Diagnose a rate denominator changing silently.",
            "The analytical question changed without a visible label.",
            "Display the current population or denominator and decide whether filtering should alter it.",
        ),
        (
            "Verify the source rows are unchanged.",
            "Filtering and rendering do not mutate original values or order.",
            "Shared immutable input makes reset and comparison predictable. Copy before sorting when needed.",
        ),
        (
            "Design a reproducible saved view.",
            "Record data identity, filters, units and aggregation policy.",
            "A screenshot lacks enough information to reconstruct the analysis. Save the decisions that generated the view.",
        ),
    ],
    r"""
const rows = Object.freeze(
  [
    { id: "A1", group: "A", value: 2 },
    { id: "A2", group: "A", value: 3 },
    { id: "B1", group: "B", value: 4 },
  ].map(Object.freeze),
);
let state = { group: "all" };
const summary = d3.select(host).append("p").attr("role", "status");
const controls = d3.select(host).append("div");
function render() {
  const visible = rows.filter((d) => state.group === "all" || d.group === state.group);
  svg
    .selectAll("rect")
    .data(visible, (d) => d.id)
    .join("rect")
    .attr("x", 100)
    .attr("y", (d, i) => 40 + i * 75)
    .attr("width", (d) => d.value * 90)
    .attr("height", 45)
    .attr("fill", "#7c3aed");
  summary.text(
    `${state.group}: ${visible.length} records; total ${d3.sum(visible, (d) => d.value)}`,
  );
  return visible;
}
const buttons = controls
  .selectAll("button")
  .data(["all", "A", "B"])
  .join("button")
  .attr("type", "button")
  .text((d) => `Show ${d}`)
  .on("click", (event, group) => {
    state = { group };
    render();
  });
render();
buttons.nodes()[1].click();
check(summary.text() === "A: 2 records; total 5", "Linked summary wrong");
check(svg.selectAll("rect").size() === 2, "Linked marks wrong");
buttons.nodes()[0].click();
check(
  render().length === 3 && rows[0].value === 2,
  "Reset or source preservation failed",
);
""",
    "https://d3js.org/d3-array/transform",
    "https://d3js.org/d3-selection/events",
)

add(
    "D3 capstone: an accessible, tested analytical dashboard",
    ["acceptance", "accessibility", "data provenance", "visual regression"],
    """The final D3 project combines a validated dataset, explicit transformations, consistent scales, keyed rendering and accessible controls. Its goal is an analytical explanation that a reader can inspect, not merely an attractive screenshot. Every visible claim should have a named source row grain, unit and aggregation policy.

Testing a visualization has several layers. Pure data tests verify filters and summaries. DOM or Canvas checks verify mark count and geometry. Interaction tests verify state changes and keyboard routes. Visual review catches clipping, illegible labels and misleading emphasis. No single screenshot or assertion covers all of these.

The reference is a small category dashboard with a filter, sorted bars, exact text values and a total summary. It uses no network input and offers a deterministic completion marker. Your independent project should change the dataset and question, then defend the encoding and limitations without copying the reference blindly.""",
    """Keep the chart’s source data, derived data and view state separate. This capstone measures its container width and uses that width in its viewBox, keeping labels at a readable 14-pixel logical size instead of shrinking a fixed 640-unit chart. A ResizeObserver schedules geometry writes on a guarded animation frame when the container changes width. Keeping writes outside the observer callback avoids a resize-notification feedback loop. It disconnects and cancels pending animation work when the preview page leaves. The table adds explicit cell padding and alignment so headers and values remain distinct. Validate IDs and finite nonnegative values before rendering. Reconcile marks by stable ID. Add a native group selector and reset. Provide a text table that remains useful without interpreting color.

The reference asserts baseline totals, filtered totals, mark counts, reset behavior and source preservation. It intentionally does not claim to automate screen-reader usability or statistical validity. Perform the manual narrow-screen, keyboard and interpretation checks before calling your own project complete.""",
    (
        "Write independent acceptance conditions",
        "These checks describe behavior rather than implementation details.",
        "const expected={allCount:4,allTotal:20,groupATotal:8};\n// Verify records, labels, totals, filter behavior and reset separately.",
        "Each assertion can fail for a meaningful user-visible error.",
    ),
    (
        "State the analytical claim",
        "A clear caption names scope and limitations.",
        'const caption="Synthetic study hours by learner group; totals describe this fixture, not a population estimate.";',
        "The chart does not turn teaching data into a real-world inference.",
    ),
    [
        (
            "Predict baseline and filtered totals.",
            "All records total20; groupA totals8.",
            "Calculate from the source rows before running. The expected values should be independent of the render code.",
        ),
        (
            "Change one value and update the independent expectations.",
            "The corresponding bar, text row and total change together.",
            "A coordinated update should preserve identity and affect only derived values implied by the source change.",
        ),
        (
            "Build a complete accessible dashboard from a blank pad.",
            "Controls, marks, text values and summary agree.",
            "The project integrates earlier mechanisms. A usable nonvisual or exact-value route is part of the deliverable.",
        ),
        (
            "Introduce a duplicate-ID failure and repair the input.",
            "Validation refuses ambiguous identity before rendering.",
            "Do not remove the identity check to obtain a success marker. Keep the failure as a regression case.",
        ),
        (
            "Perform keyboard and narrow-screen review.",
            "All controls are reachable, labels readable and essential information available without hover.",
            "Automated checks cannot prove the full human experience. Record actual observations and unresolved issues.",
        ),
        (
            "Defend the finished analysis and its evidence limits.",
            "Explain data grain, cleaning, scales, aggregation, interactions and untested surfaces.",
            "Expert practice includes knowing what the chart does not establish. Separate software correctness from statistical inference and usability evidence.",
        ),
    ],
    r"""
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
  summary.text(
    `${visible.length} records; total ${d3.sum(visible, (d) => d.hours)} hours`,
  );
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
  .text(
    "Synthetic study hours by learner group; this fixture is not a population estimate.",
  );
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
addEventListener("pagehide", () => {
  observer.disconnect();
  if (resizeFrame !== 0) cancelAnimationFrame(resizeFrame);
}, { once: true });
""",
    "https://d3js.org/what-is-d3",
    "https://www.w3.org/WAI/tutorials/images/complex/",
)


# Editorial normalization affects prose fields only, never code examples/references.
def _prose(value):
    import re

    prefixes = r"A|Client|Depth|Diagnose|Draw|HTTP|Layer|Pod|Service|Values|Width|advances|and|app|are|as|backend|become|bind|binding|by|containerPort|coordinate|for|from|guarantee|have|height|listener|node|nodePort|of|often|port|range|remains|scale|second|segment|through|to|total|totals|use|values|why"
    value = re.sub(r"\b(" + prefixes + r")(?=\d)", r"\1 ", value)
    value = re.sub(r",(?=\d)", ", ", value)
    return value


LESSONS = [
    (
        _prose(title),
        concepts,
        _prose(mental),
        _prose(anatomy),
        [(_prose(h), _prose(b), code, _prose(expected)) for h, b, code, expected in examples],
        [tuple(_prose(v) for v in task) for task in tasks],
        reference,
        refs,
    )
    for title, concepts, mental, anatomy, examples, tasks, reference, refs in LESSONS
]
