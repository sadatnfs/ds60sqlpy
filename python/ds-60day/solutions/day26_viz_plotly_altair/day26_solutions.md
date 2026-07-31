# Day 26 — Solutions: Interactive Visualization (Plotly / Altair)

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **interactive visual encodings, bounded interaction, and portable HTML export**. Predict each named
result before comparing your attempt with its matching assertions.

Interaction is useful when it helps a reader answer a question—inspect a
point, filter a segment, zoom a dense range, or compare parameter
choices. It is not a substitute for a clear initial view. The chart
still needs an honest title, visible axes/legend, sensible defaults,
units, and a bounded amount of data.

Plotly builds figure objects directly; Altair declares how fields map
to visual encodings and transformations. Both can produce HTML, but
portability depends on whether JavaScript and data are embedded or
loaded from a Content Delivery Network (CDN). For offline course use,
export self-contained content and test it while disconnected.

### Vocabulary used in the worked answers

- **interaction:** a reader action that changes or reveals a chart view.
- **tooltip:** details shown for a hovered/focused mark.
- **selection:** a user-controlled set of marks or values.
- **parameter:** a bounded value controlling an interactive expression.
- **CDN:** a remote network service supplying shared assets such as JavaScript.
- **self-contained HTML:** a file embedding the assets needed to work offline.

### How to compare an answer

For this lesson's **interactive visual encodings, bounded interaction, and portable HTML export** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–2 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Create an interactive histogram whose bin count can be changed only within sensible bounds. **Plotly route:** isolate a builder accepting `bins`; **Altair route:** bind a range input to a parameter. **Expected behavior:** changing bins alters aggregation without changing the underlying observations. **Verify:** test minimum/default/maximum settings and show the displayed total count remains the number of non-missing values.

**Reasoning:** Implement this exact contract as written: Create an interactive histogram whose bin count can be changed only within sensible bounds. Plotly route: isolate a builder accepting `bins`; Altair route: bind a range input to a parameter. Expected behavior: changing bins alters aggregation without changing the underlying observations. Keep the prompt's named data and constraints visible in the code, then establish this specific result: test minimum/default/maximum settings and show the displayed total count remains the number of non-missing values. That connects the answer to interactive visual encodings, bounded interaction, and portable HTML export.

```python
import pandas as pd
import plotly.express as px


def histogram(frame: pd.DataFrame, *, bins: int):
    if not 2 <= bins <= 100:
        raise ValueError("bins must be between 2 and 100")
    return px.histogram(frame, x="value", nbins=bins, title="Value distribution")


frame = pd.DataFrame({"value": [1, 1, 2, 3, 5, 8]})
source_snapshot = frame.copy(deep=True)
for bins in (2, 10, 100):
    figure = histogram(frame, bins=bins)
    assert figure.layout.title.text == "Value distribution"
    assert len(figure.data[0].x) == frame["value"].notna().sum()
    pd.testing.assert_frame_equal(frame, source_snapshot)

for invalid_bins in (1, 101):
    try:
        histogram(frame, bins=invalid_bins)
    except ValueError as error:
        assert "between 2 and 100" in str(error)
    else:
        raise AssertionError("out-of-range bins should fail")
```

The source observations do not change; only the displayed aggregation
granularity changes.

**Verification evidence:** test minimum/default/maximum settings and show the displayed total count remains the number of non-missing values.

### Exercise 2 — worked answer

**Learner contract:** Export the chart to a self-contained HTML file under an ignored learner artifact directory. **Constraints:** embed required JavaScript/data, use no remote font/analytics dependency, and document payload size. **Verify:** disconnect network access or use browser offline mode, reopen the file, and confirm tooltips/controls still function.

**Reasoning:** Implement this exact contract as written: Export the chart to a self-contained HTML file under an ignored learner artifact directory. Constraints: embed required JavaScript/data, use no remote font/analytics dependency, and document payload size. Keep the prompt's named data and constraints visible in the code, then establish this specific result: disconnect network access or use browser offline mode, reopen the file, and confirm tooltips/controls still function. That connects the answer to interactive visual encodings, bounded interaction, and portable HTML export.

```python
from pathlib import Path
import re

destination = Path("artifacts/day26/histogram.html")
destination.parent.mkdir(parents=True, exist_ok=True)
figure.write_html(destination, include_plotlyjs=True, full_html=True)
html = destination.read_text(encoding="utf-8")
assert "<html" in html.lower()
assert "Value distribution" in html
assert re.search(
    r"<script[^>]+src=['\"]https?://",
    html,
    flags=re.IGNORECASE,
) is None
payload_bytes = destination.stat().st_size
assert payload_bytes > 100_000
```

`include_plotlyjs=True` embeds the runtime so the file remains
interactive without a Content Delivery Network. Record
`payload_bytes` when comparing portability with file size; browser
offline mode should still show hover tooltips and toolbar controls.

**Verification evidence:** disconnect network access or use browser offline mode, reopen the file, and confirm tooltips/controls still function.

## Exercises 3–7 — Expanded mastery answers

### Exercise 3 — answer contract

**Learner contract:** **Prediction:** Predict the portability difference between Plotly HTML that embeds its JavaScript and HTML that loads a CDN copy. **Progressive hint:** A CDN reference needs network access when opened. **Verify:** Export embedded and CDN versions, inspect asset references/file sizes, and confirm only the embedded version remains interactive with network disabled.

**Reasoning:** Predict this named state change before running it: Prediction: Predict the portability difference between Plotly HTML that embeds its JavaScript and HTML that loads a CDN copy. Progressive hint: A CDN reference needs network access when opened. Then compare the prediction with this proof target: Export embedded and CDN versions, inspect asset references/file sizes, and confirm only the embedded version remains interactive with network disabled. This makes interactive visual encodings, bounded interaction, and portable HTML export observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Export embedded and CDN versions, inspect asset references/file sizes, and confirm only the embedded version remains interactive with network disabled.

### Exercise 4 — answer contract

**Learner contract:** **Tracing:** Trace one row into x, y, color, and hover fields and explain what the reader can infer from each visible encoding. **Progressive hint:** A field retained only in source data is not visibly encoded. **Verify:** For one known row, assert its x/y values, visible group, and bounded hover fields; explain one source field intentionally not encoded.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace one row into x, y, color, and hover fields and explain what the reader can infer from each visible encoding. Progressive hint: A field retained only in source data is not visibly encoded. Record the named value, shape, label, or iterator position needed to establish: For one known row, assert its x/y values, visible group, and bounded hover fields; explain one source field intentionally not encoded. The trace exposes interactive visual encodings, bounded interaction, and portable HTML export directly.

**Evidence to locate in the grouped implementation:** For one known row, assert its x/y values, visible group, and bounded hover fields; explain one source field intentionally not encoded.

### Exercise 5 — answer contract

**Learner contract:** **Implementation:** Implement a Plotly scatter builder that validates required columns, bounds hover fields, and returns a figure without writing files. **Progressive hint:** Separate figure construction from export. **Verify:** Test valid data and missing-column data; assert the valid builder returns a figure with expected traces while the invalid path lists exact missing names and writes nothing.

**Reasoning:** Trace the concrete values in this contract one step at a time: Implementation: Implement a Plotly scatter builder that validates required columns, bounds hover fields, and returns a figure without writing files. Progressive hint: Separate figure construction from export. Record the named value, shape, label, or iterator position needed to establish: Test valid data and missing-column data; assert the valid builder returns a figure with expected traces while the invalid path lists exact missing names and writes nothing. The trace exposes interactive visual encodings, bounded interaction, and portable HTML export directly.

**Evidence to locate in the grouped implementation:** Test valid data and missing-column data; assert the valid builder returns a figure with expected traces while the invalid path lists exact missing names and writes nothing.

### Exercise 6 — answer contract

**Learner contract:** **Debugging:** Repair a chart-builder failure caused by a misspelled column and return an actionable error listing missing names. **Progressive hint:** Validate the schema before calling the plotting library. **Verify:** Pass two misspelled/missing fields and assert one actionable pre-plot error names both before Plotly receives the frame.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair a chart-builder failure caused by a misspelled column and return an actionable error listing missing names. Progressive hint: Validate the schema before calling the plotting library. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Pass two misspelled/missing fields and assert one actionable pre-plot error names both before Plotly receives the frame. The diagnosis depends on interactive visual encodings, bounded interaction, and portable HTML export.

**Evidence to locate in the grouped implementation:** Pass two misspelled/missing fields and assert one actionable pre-plot error names both before Plotly receives the frame.

### Exercise 7 — answer contract

**Learner contract:** **Edge case and explanation:** Design deterministic sampling or aggregation for a million-row interactive chart while preserving important groups. **Progressive hint:** Browser rendering and HTML size are part of the data contract. **Verify:** Apply the deterministic reduction twice and assert identical rows/group representation, bounded payload size, and retained important-group counts.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Design deterministic sampling or aggregation for a million-row interactive chart while preserving important groups. Progressive hint: Browser rendering and HTML size are part of the data contract. Values below, at, and above the named boundary must produce the evidence Apply the deterministic reduction twice and assert identical rows/group representation, bounded payload size, and retained important-group counts. Those cases show how interactive visual encodings, bounded interaction, and portable HTML export behaves at its edge.

**Evidence to locate in the grouped implementation:** Apply the deterministic reduction twice and assert identical rows/group representation, bounded payload size, and retained important-group counts.

## Expanded mastery lab solutions

Use interaction to answer a question, not to decorate a chart. Keep tooltips, filters, payload size, and offline HTML behavior intentional.

### Shared implementation for Exercises 3–4 — Portability and visible encodings

Embedded Plotly JavaScript makes a larger standalone file that works offline;
a CDN-based file is smaller but needs network access. A reader can interpret
only fields encoded on axes, color/shape, facets, labels, or tooltips.

### Shared implementation for Exercises 5–7 — Validate before rendering

```python
from collections.abc import Sequence

import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure


def build_scatter(
    frame: pd.DataFrame,
    *,
    x: str,
    y: str,
    color: str | None = None,
    hover: Sequence[str] = (),
) -> Figure:
    """Return a validated scatter figure without I/O side effects."""

    requested = [x, y, *([color] if color else []), *hover]
    missing = sorted(set(requested) - set(frame.columns))
    if missing:
        raise ValueError(f"missing chart columns: {', '.join(missing)}")
    bounded_hover = list(hover)[:5]
    return px.scatter(frame, x=x, y=y, color=color, hover_data=bounded_hover)


sample = pd.DataFrame(
    {"bill": [10, 20, 30], "tip": [1, 4, 5], "meal": ["L", "D", "D"]}
)
figure = build_scatter(sample, x="bill", y="tip", color="meal", hover=["meal"])
assert len(figure.data) == 2
```

For very large data, use a fixed-seed stratified sample by important groups or
aggregate to meaningful bins. Report the original and displayed row counts.
When exporting for offline use, choose an embedded-JavaScript mode deliberately
and test the file with networking disabled.
