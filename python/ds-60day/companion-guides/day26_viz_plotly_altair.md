# Day 26 — Interactive Visualization with Plotly and Altair

**Level:** Intermediate

Interaction should answer a reader question—inspect a point, filter a segment,
or adjust a meaningful parameter—not decorate a chart.

## Learning objectives

By the end of this lesson, you can:

- create an interactive chart with useful hover information;
- add a bounded selection or parameter;
- label encodings so the chart stands alone;
- export a self-contained HTML file that works offline;
- explain the size/security trade-offs of embedded data and JavaScript.

## Prerequisites

Complete Day 25 (`python-25`): chart selection, visual encodings, labels, and
static export. Plotly and Altair are in the `data` dependency group.

## Vocabulary and mental model

- **Tooltip:** details shown for a hovered mark.
- **Selection:** interactive subset of marks/data.
- **Parameter:** user-controlled value that changes a transform or encoding.
- **Renderer:** component that turns a chart specification into visible output.
- **Self-contained HTML:** document embeds required data and JavaScript.
- **CDN:** network-hosted asset; smaller output, but not offline.

## Worked example

```python
from pathlib import Path

import pandas as pd
import plotly.express as px

frame = pd.DataFrame(
    {"day": ["Mon", "Tue", "Wed"], "orders": [12, 18, 15], "returns": [1, 2, 1]}
)
figure = px.scatter(
    frame,
    x="orders",
    y="returns",
    hover_name="day",
    title="Orders and returns by day",
)
output = Path("artifacts") / "orders_returns.html"
output.parent.mkdir(parents=True, exist_ok=True)
figure.write_html(output, include_plotlyjs=True)
```

Embedding Plotly's JavaScript makes the file larger but usable with no network.
Do not use `include_plotlyjs="cdn"` for an offline deliverable.

## Dataset note

The notebook uses Seaborn's `tips` sample and therefore may download/cache it on
first use. The constructed example above avoids that dependency.

## Exercises and progressive hints

1. Create an interactive histogram whose bin choice can be changed within
   sensible bounds. **Hint:** in Altair, bind a range input to a parameter; in
   Plotly, isolate figure construction in a function accepting a bin count.
2. Save the chart as HTML and open it in a browser. **Hint:** disconnect from
   the network before the final check and inspect whether all required
   JavaScript/data were embedded.

### Additional mastery practice

Use interaction to answer a question, not to decorate a chart. Keep tooltips, filters, payload size, and offline HTML behavior intentional.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict the portability difference between Plotly HTML that embeds its JavaScript and HTML that loads a CDN copy.
   **Progressive hint:** A CDN reference needs network access when opened.
4. **Tracing:** Trace one row into x, y, color, and hover fields and explain what the reader can infer from each visible encoding.
   **Progressive hint:** A field retained only in source data is not visibly encoded.
5. **Implementation:** Implement a Plotly scatter builder that validates required columns, bounds hover fields, and returns a figure without writing files.
   **Progressive hint:** Separate figure construction from export.
6. **Debugging:** Repair a chart-builder failure caused by a misspelled column and return an actionable error listing missing names.
   **Progressive hint:** Validate the schema before calling the plotting library.
7. **Edge case and explanation:** Design deterministic sampling or aggregation for a million-row interactive chart while preserving important groups.
   **Progressive hint:** Browser rendering and HTML size are part of the data contract.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.


## Self-check

- What question does each interaction answer?
- Which fields belong in a tooltip, and which could expose sensitive data?
- Why can a self-contained Plotly file be several megabytes?
- What must be embedded for an HTML chart to work offline?

Expected behavior: controls remain within valid bounds, hover text is useful,
and the exported file still renders with networking disabled.

## Common pitfalls and diagnosis

- **Notebook chart is blank:** confirm the selected kernel, renderer, and
  installed package; test HTML export separately.
- **Export works only online:** remove CDN dependencies and embed the library.
- **The HTML is unexpectedly huge:** aggregate/sample intentionally, limit
  fields, and document that trade-off rather than silently dropping data.
- **Tooltips expose row-level identifiers:** include only fields needed to
  interpret the mark.
- **An interaction changes appearance but not meaning:** connect it to a stated
  analytical question or remove it.

## Continue

- [Open the learner notebook](../notebooks/day26_viz_plotly_altair.ipynb)
- [Check the separate solution](../solutions/day26_viz_plotly_altair/day26_solutions.md)
- [Next: Day 27 — Geospatial/domain visualization](day27_geospatial_or_domain_viz.md)
