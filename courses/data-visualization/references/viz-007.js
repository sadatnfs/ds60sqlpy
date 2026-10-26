// Durable offline Plotly counterparts. No imports, fetches or external assets.
// The subject builder appends a selected case invocation to this source fragment.
/* exported specifications, renderCase */
function requireCondition(condition, message) {
  if (!condition) throw new Error(message);
}

function envelopeIndices(values, block = 100) {
  const keep = new Set([0, values.length - 1]);
  for (let start = 0; start < values.length; start += block) {
    let low = start;
    let high = start;
    for (let i = start; i < Math.min(start + block, values.length); i += 1) {
      if (values[i] < values[low]) low = i;
      if (values[i] > values[high]) high = i;
    }
    keep.add(low);
    keep.add(high);
  }
  return [...keep].sort((a, b) => a - b);
}

const specifications = {
  1() {
    const records = [
      ["u1", "Alpha", 2],
      ["u2", "Beta", 5],
      ["u3", "Gamma", 3],
    ];
    const ordered = [...records].sort((a, b) => b[2] - a[2]);
    requireCondition(
      ordered[0][0] === "u2" && ordered.reduce((s, r) => s + r[2], 0) === 10,
      "Row identity changed",
    );
    return {
      title: "Three measured completion times",
      description:
        "Beta takes five hours, Gamma three and Alpha two. These are three records, not uncertainty estimates.",
      columns: ["record", "team", "hours"],
      rows: ordered,
      data: [
        {
          type: "bar",
          x: ordered.map((r) => r[1]),
          y: ordered.map((r) => r[2]),
          customdata: ordered.map((r) => [r[0]]),
          text: ordered.map((r) => r[2]),
          textposition: "outside",
          marker: { color: "#176b87" },
          hovertemplate: "%{x}: %{y:.1f} hours (record %{customdata[0]})<extra></extra>",
        },
      ],
      layout: {
        xaxis: { title: { text: "Team" } },
        yaxis: { title: { text: "Elapsed hours" }, rangemode: "tozero" },
      },
    };
  },
  2() {
    const raw = [1, 1, 2, 2, 3, 4, 6, 8, 10, 12, null];
    const values = raw.filter((value) => value !== null);
    const edges = [0, 3, 6, 9, 13];
    const widths = edges.slice(1).map((v, i) => v - edges[i]);
    const counts = widths.map(
      (_, i) =>
        values.filter((v) => v >= edges[i] && (v < edges[i + 1] || (i === 3 && v === edges[i + 1])))
          .length,
    );
    const density = counts.map((count, i) => count / (values.length * widths[i]));
    const unique = [...new Set(values)].sort((a, b) => a - b);
    const cumulative = unique.map(
      (value) => values.filter((v) => v <= value).length / values.length,
    );
    requireCondition(JSON.stringify(counts) === "[4,2,2,2]", "Histogram boundaries changed");
    requireCondition(
      Math.abs(density.reduce((s, d, i) => s + d * widths[i], 0) - 1) < 1e-12,
      "Density must integrate to one",
    );
    return {
      title: "Distribution of ten observed durations",
      description:
        "One missing value is excluded, not coded zero. Unequal-bin density integrates to one and the ECDF reaches one.",
      columns: ["lower", "upper", "count", "density"],
      rows: counts.map((c, i) => [edges[i], edges[i + 1], c, density[i]]),
      data: [
        {
          type: "bar",
          x: widths.map((w, i) => edges[i] + w / 2),
          y: density,
          width: widths,
          name: "density",
        },
        {
          type: "scatter",
          x: [0, ...unique],
          y: [0, ...cumulative],
          xaxis: "x2",
          yaxis: "y2",
          mode: "lines+markers",
          line: { shape: "hv" },
          name: "ECDF",
          marker: { symbol: "square" },
        },
      ],
      layout: {
        grid: { rows: 1, columns: 2, pattern: "independent" },
        xaxis: { title: { text: "Duration (minutes)" } },
        yaxis: { title: { text: "Probability per minute" } },
        xaxis2: { title: { text: "Duration (minutes)" } },
        yaxis2: { title: { text: "Fraction at or below" }, range: [0, 1.05] },
      },
    };
  },
  3() {
    const labels = ["North", "Central", "South"];
    const effect = [-0.4, 0.2, 0.8];
    const se = [0.1, 0.3, 0.2];
    const lower = effect.map((v, i) => v - 1.96 * se[i]);
    const upper = effect.map((v, i) => v + 1.96 * se[i]);
    requireCondition(
      lower[2] > 0 && lower[1] < 0 && upper[1] > 0,
      "Interval interpretation changed",
    );
    return {
      title: "Regional effects with marginal intervals",
      description:
        "Separate normal-approximation 95% confidence intervals describe mean differences. They are not simultaneous intervals or individual outcome ranges.",
      columns: ["region", "effect", "lower95", "upper95"],
      rows: labels.map((l, i) => [l, effect[i], lower[i], upper[i]]),
      data: [
        {
          type: "scatter",
          x: effect,
          y: labels,
          mode: "markers",
          marker: { symbol: "diamond", size: 11 },
          error_x: {
            type: "data",
            array: se.map((v) => 1.96 * v),
            arrayminus: se.map((v) => 1.96 * v),
            symmetric: false,
          },
          customdata: labels.map((_, i) => [lower[i], upper[i]]),
          hovertemplate:
            "%{y}: %{x:.3f}; CI [%{customdata[0]:.3f}, %{customdata[1]:.3f}]<extra></extra>",
        },
      ],
      layout: {
        xaxis: { title: { text: "Mean difference (points)" }, range: [-0.8, 1.4] },
        yaxis: { title: { text: "Prespecified region" } },
        shapes: [
          {
            type: "line",
            x0: 0,
            x1: 0,
            y0: 0,
            y1: 1,
            yref: "paper",
            line: { dash: "dash", color: "#555" },
          },
        ],
      },
    };
  },
  4() {
    const records = Array.from({ length: 8 }, (_, i) => [
      `u${i}`,
      i < 4 ? "A" : "B",
      i,
      2 * i + (i % 3),
    ]);
    const data = ["A", "B"].map((group, i) => {
      const subset = records.filter((row) => row[1] === group);
      return {
        type: "scatter",
        x: subset.map((r) => r[2]),
        y: subset.map((r) => r[3]),
        mode: "markers",
        name: group,
        customdata: subset.map((r) => [r[0], r[1]]),
        marker: { symbol: i === 0 ? "circle" : "square", size: 12 },
        hovertemplate:
          "%{customdata[0]} (%{customdata[1]}): baseline %{x}, outcome %{y}<extra></extra>",
      };
    });
    requireCondition(
      data.every((trace) => trace.x.length === 4),
      "Expected four users per group",
    );
    return {
      title: "Inspect groups without changing the source population",
      description:
        "The chart filter is exploratory. The table always lists all eight source records; selection is not a randomized subgroup experiment.",
      columns: ["user", "group", "baseline", "outcome"],
      rows: records,
      data,
      groupFilter: true,
      layout: {
        xaxis: { title: { text: "Pretreatment activity" } },
        yaxis: { title: { text: "Observed outcome" } },
        uirevision: "viz-004-fixture-v1",
      },
    };
  },
  5() {
    const historyDates = Array.from(
      { length: 6 },
      (_, i) => `2026-01-${String(i + 1).padStart(2, "0")}`,
    );
    const futureDates = ["2026-01-07", "2026-01-08", "2026-01-09"];
    const forecast = [16, 17, 18],
      actual = [17, 16, 19],
      lower = [14, 15, 16],
      upper = [18, 19, 20];
    const rmse = Math.sqrt(actual.reduce((s, a, i) => s + (a - forecast[i]) ** 2, 0) / 3);
    requireCondition(
      rmse === 1 && futureDates[0] > historyDates[5],
      "Forecast boundary or loss is wrong",
    );
    return {
      title: "A forecast frozen before outcomes arrived",
      description:
        "History ends January 6. Forecast RMSE is one on three later outcomes. The plus/minus two band is illustrative and has no asserted coverage calibration.",
      columns: ["date", "forecast", "actual", "lower", "upper"],
      rows: futureDates.map((d, i) => [d, forecast[i], actual[i], lower[i], upper[i]]),
      data: [
        {
          type: "scatter",
          x: historyDates,
          y: [10, 11, 12, 13, 14, 15],
          mode: "lines+markers",
          name: "Available history",
        },
        {
          type: "scatter",
          x: [...futureDates, ...[...futureDates].reverse()],
          y: [...upper, ...[...lower].reverse()],
          fill: "toself",
          fillcolor: "rgba(23,107,135,0.15)",
          line: { width: 0 },
          hoverinfo: "skip",
          name: "Illustrative band",
        },
        {
          type: "scatter",
          x: futureDates,
          y: forecast,
          mode: "lines+markers",
          line: { dash: "dash" },
          name: "Frozen forecast",
        },
        {
          type: "scatter",
          x: futureDates,
          y: actual,
          mode: "markers",
          marker: { symbol: "x" },
          name: "Later observed",
        },
      ],
      layout: {
        xaxis: { type: "date", title: { text: "Event date" } },
        yaxis: { title: { text: "Daily demand (units)" } },
      },
    };
  },
  6() {
    const actual = [1, 2, 3, 4, 5, 6, 7, 8];
    const ea = [0.2, -0.2, 0.5, -0.5, 0.1, -0.1, 1, -1];
    const eb = [0.4, -0.4, 0.6, -0.6, 0.2, -0.2, 1.5, -1.5];
    const a = actual.map((v, i) => v + ea[i]),
      b = actual.map((v, i) => v + eb[i]);
    const difference = ea.map((v, i) => v * v - eb[i] ** 2);
    requireCondition(
      Math.abs(difference.reduce((s, v) => s + v, 0) / 8 + 0.3775) < 1e-12,
      "Paired loss arithmetic changed",
    );
    return {
      title: "A paired model comparison",
      description:
        "Both models use the same eight held-out users and common axes. Negative squared-loss differences favor A; population uncertainty remains unestimated here.",
      columns: ["user", "observed", "A", "B", "A_loss_minus_B"],
      rows: actual.map((v, i) => [`u${i}`, v, a[i], b[i], difference[i]]),
      data: [
        {
          type: "scatter",
          x: actual,
          y: a,
          mode: "markers",
          name: "Model A",
          marker: { symbol: "circle" },
        },
        {
          type: "scatter",
          x: actual,
          y: b,
          mode: "markers",
          name: "Model B",
          marker: { symbol: "square" },
        },
        {
          type: "scatter",
          x: [0, 10],
          y: [0, 10],
          mode: "lines",
          line: { dash: "dash" },
          name: "Identity",
        },
        {
          type: "bar",
          x: actual.map((_, i) => `u${i}`),
          y: difference,
          xaxis: "x2",
          yaxis: "y2",
          name: "A loss minus B loss",
        },
      ],
      layout: {
        grid: { rows: 1, columns: 2, pattern: "independent" },
        xaxis: { title: { text: "Observed" }, range: [0, 10] },
        yaxis: { title: { text: "Predicted" }, range: [0, 10] },
        xaxis2: { title: { text: "Held-out user" } },
        yaxis2: { title: { text: "Squared units" } },
      },
    };
  },
  7() {
    const values = Array.from({ length: 5000 }, (_, i) => Math.sin(i / 40));
    values[2473] = 12;
    const stride = Array.from({ length: 50 }, (_, i) => 100 * i);
    const keep = envelopeIndices(values);
    requireCondition(
      keep.includes(2473) && !stride.includes(2473) && keep.length <= 102,
      "Extrema preservation failed",
    );
    return {
      title: "Preserve extrema when reducing displayed points",
      description:
        "Regular stride misses the spike at sample 2473. The min/max envelope preserves block extrema, not every frequency, mean or intermediate shape. This is SVG reduction, not a GPU performance claim.",
      columns: ["representation", "points", "maximum", "spike_retained"],
      rows: [
        ["original", 5000, 12, true],
        ["stride", 50, Math.max(...stride.map((i) => values[i])), false],
        ["envelope", keep.length, 12, true],
      ],
      data: [
        {
          type: "scatter",
          x: stride,
          y: stride.map((i) => values[i]),
          mode: "lines+markers",
          line: { dash: "dot" },
          name: "Regular stride",
        },
        {
          type: "scatter",
          x: keep,
          y: keep.map((i) => values[i]),
          mode: "lines",
          name: "Min/max envelope",
        },
      ],
      layout: {
        xaxis: { title: { text: "Sample index" } },
        yaxis: { title: { text: "Measured amplitude" } },
      },
    };
  },
  8() {
    const labels = ["completed", "pending", "failed"],
      counts = [8, 3, 1];
    requireCondition(counts.reduce((s, n) => s + n, 0) === 12, "Status count is wrong");
    return {
      title: "Twelve jobs at a declared observation cutoff",
      description:
        "Eight completed, three pending and one failed. Pending is not failure. Labels, patterns and this native table preserve meaning without relying only on color. JSON export preserves a figure specification, not a rendered screenshot.",
      columns: ["status", "count"],
      rows: labels.map((l, i) => [l, counts[i]]),
      exportSpec: true,
      data: [
        {
          type: "bar",
          x: labels,
          y: counts,
          text: counts,
          textposition: "outside",
          marker: { color: ["#176b87", "#a66000", "#a61c3c"], pattern: { shape: ["", "/", "x"] } },
        },
      ],
      layout: {
        xaxis: { title: { text: "Recorded status" } },
        yaxis: { title: { text: "Jobs" }, rangemode: "tozero" },
      },
    };
  },
};

async function renderCase(spec, marker) {
  requireCondition(
    typeof window.Plotly?.newPlot === "function",
    "Use the prepared Plotly browser preview",
  );
  const root = document.getElementById("chart");
  const output = document.getElementById("output");
  root.replaceChildren();
  const description = document.createElement("p");
  description.textContent = spec.description;
  root.append(description);
  const status = document.createElement("p");
  status.setAttribute("role", "status");
  status.textContent = "All source records shown in the table.";
  const graph = document.createElement("div");
  graph.style.minHeight = "440px";
  graph.setAttribute("role", "group");
  graph.setAttribute("aria-label", spec.title);
  root.append(graph, status);
  const table = document.createElement("table");
  const caption = table.createCaption();
  caption.textContent = `${spec.title}: source values`;
  const header = table.createTHead().insertRow();
  for (const column of spec.columns) {
    const cell = document.createElement("th");
    cell.scope = "col";
    cell.textContent = column;
    header.append(cell);
  }
  const body = table.createTBody();
  for (const row of spec.rows) {
    const tr = body.insertRow();
    for (const value of row) tr.insertCell().textContent = String(value);
  }
  const tableRegion = document.createElement("div");
  tableRegion.style.maxWidth = "100%";
  tableRegion.style.overflowX = "auto";
  tableRegion.append(table);
  root.append(tableRegion);
  const titleLines = [];
  for (const word of spec.title.split(" ")) {
    const last = titleLines.length - 1;
    if (last < 0 || titleLines[last].length + word.length + 1 > 28) titleLines.push(word);
    else titleLines[last] += ` ${word}`;
  }
  const layout = {
    title: {
      text: titleLines.join("<br>"),
      font: { size: 16 },
      x: 0,
      xanchor: "left",
      automargin: true,
    },
    height: 440,
    margin: { l: 65, r: 25, t: 90, b: 65 },
    paper_bgcolor: "#fff",
    plot_bgcolor: "#fff",
    ...spec.layout,
  };
  await window.Plotly.newPlot(graph, spec.data, layout, { responsive: true, displaylogo: false });
  if (spec.groupFilter) {
    const controls = document.createElement("fieldset");
    const legend = document.createElement("legend");
    legend.textContent = "Visible chart group";
    controls.append(legend);
    for (const name of ["All", "A", "B"]) {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = name === "All" ? "All groups" : `Group ${name}`;
      button.dataset.group = name;
      button.setAttribute("aria-pressed", String(name === "All"));
      button.addEventListener("click", async () => {
        const visible = ["A", "B"].map((group) => name === "All" || name === group);
        await window.Plotly.restyle(graph, { visible }, [0, 1]);
        for (const control of controls.querySelectorAll("button")) {
          control.setAttribute("aria-pressed", String(control.dataset.group === name));
        }
        status.textContent = `Chart group: ${name}. The source table remains complete.`;
      });
      controls.append(button);
    }
    root.insertBefore(controls, graph);
    graph.on("plotly_selected", (event) => {
      const ids = (event?.points ?? []).map((point) => point.customdata?.[0]).filter(Boolean);
      status.textContent = ids.length
        ? `Selected IDs: ${[...new Set(ids)].join(", ")}`
        : "No selected points.";
    });
  }
  if (spec.exportSpec) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = "Show figure JSON";
    const text = document.createElement("textarea");
    text.readOnly = true;
    text.setAttribute("aria-label", "Figure specification JSON");
    text.rows = 8;
    text.style.width = "100%";
    text.style.boxSizing = "border-box";
    button.addEventListener("click", () => {
      const serialized = JSON.stringify(
        {
          data: spec.data,
          layout,
          description: spec.description,
          table: { columns: spec.columns, rows: spec.rows },
        },
        null,
        2,
      );
      requireCondition(
        JSON.parse(serialized).data[0].y.reduce((s, n) => s + n, 0) === 12,
        "Export changed counts",
      );
      text.value = serialized;
      status.textContent =
        "Reviewable figure JSON is ready to copy. No network request or download occurred.";
    });
    root.append(button, text);
  }
  const cleanup = () => window.Plotly.purge(graph);
  window.addEventListener("pagehide", cleanup, { once: true });
  requireCondition(table.tBodies[0].rows.length === spec.rows.length, "Accessible table lost rows");
  requireCondition(graph.querySelector(".main-svg") !== null, "No Plotly SVG was rendered");
  output.textContent = `${marker}\n${spec.description}`;
  console.log(marker);
}

await renderCase(specifications[7](), "viz-007 Plotly complete");
