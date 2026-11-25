# Day 26 Solutions: Interactive Visualization with Plotly and Altair

The classroom displays captured Plotly figures. Altair examples here build
and validate a Vega-Lite specification, which the reference publishes as a
structured JSON report. Actual Vega-Lite interaction belongs to the separately
prepared contributor notebook/export renderer; a validated specification alone
does not establish that a browser interaction was tested. Use the Plotly route
for native classroom interaction. A generated HTML filename is inside the
execution environment and is not automatically a download to your host.

Vega-Lite does not accept a variable parameter directly as a binning `maxbins`
value. The reference uses a bounded menu of constant-bin layers and filters to
the selected layer. `maxbins` is an approximate upper limit. See the official
[adjustable histogram example](https://altair-viz.github.io/gallery/interactive_bin_size.html)
for the underlying mechanism. Self-contained Plotly HTML uses its bundled
JavaScript; Altair HTML needs deliberately prepared Vega assets for offline use.


**Offline teaching data:** the `restaurant-bills` [synthetic fixture](../../../fixtures/README.md) is invented, so its numbers prove methods, not facts.


<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **interactive visual encodings, bounded interaction, and portable HTML export**. Predict each named
result before comparing your attempt with its matching assertions.

Interaction is useful when it helps a reader answer a question, inspect a
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

## Exercises 1-2: Worked answers

### Exercise 1: worked answer

**Learner contract:** Create an interactive histogram whose bin count can be changed only within sensible bounds. **Plotly route:** isolate a builder accepting `bins`; **Altair route:** bind a range input to a parameter. **Expected behavior:** changing bins alters aggregation without changing the underlying observations. **Verify:** test minimum/default/maximum settings and show the displayed total count remains the number of non-missing values.

**Reasoning:** Validating `bins` before plotting turns an unreasonable request into a clear `ValueError` instead of a misleading chart: one bin hides the shape, and hundreds of bins on six values show only noise. Changing `bins` changes only how the observations are grouped, so for the minimum, default, and maximum settings the test checks that the trace still holds all six values and that the source frame is unchanged. The out-of-range values 1 and 101 are tested explicitly because boundaries are where off-by-one mistakes hide.

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

### Exercise 2: worked answer

**Learner contract:** Export the chart to a self-contained HTML file under an ignored learner artifact directory. **Constraints:** embed required JavaScript/data, use no remote font/analytics dependency, and document payload size. **Verify:** disconnect network access or use browser offline mode, reopen the file, and confirm tooltips/controls still function.

**Reasoning:** `include_plotlyjs=True` writes the whole plotly.js library into the HTML file, so the chart works offline and where external scripts are blocked; the price is a file of several megabytes, which is why the payload size is recorded. The regular expression checks that no `<script>` tag loads code from an external `http` or `https` address, which would break offline use. Opening the file in a browser with networking disabled remains the final, manual check that tooltips and toolbar controls still work.

```python
from pathlib import Path
import re

destination = Path("artifacts/day26/histogram.html")
destination.parent.mkdir(parents=True, exist_ok=True)
figure.write_html(destination, include_plotlyjs=True, full_html=True)
html = destination.read_text(encoding="utf-8")
assert "<html" in html.lower()
assert "Value distribution" in html
assert (
    re.search(
        r"<script[^>]+src=['\"]https?://",
        html,
        flags=re.IGNORECASE,
    )
    is None
)
payload_bytes = destination.stat().st_size
assert payload_bytes > 100_000
```

`include_plotlyjs=True` embeds the runtime so the file remains
interactive without a Content Delivery Network. Record
`payload_bytes` when comparing portability with file size; browser
offline mode should still show hover tooltips and toolbar controls.

## Exercises 3-7: Expanded mastery answers

### Exercise 3: answer contract

**Learner contract:** **Prediction:** Predict the portability difference between Plotly HTML that embeds its JavaScript and HTML that loads a CDN copy. **Progressive hint:** A CDN reference needs network access when opened. **Verify:** Export embedded and CDN versions, inspect asset references/file sizes, and confirm only the embedded version remains interactive with network disabled.

**Reasoning:** An HTML file with embedded JavaScript carries the full plotly.js library, so it is large but self-contained; a file written with `include_plotlyjs="cdn"` holds only a `<script>` tag that downloads the library when opened, so it is tiny but draws nothing without network access. The shared implementation for Exercises 3-4 writes both versions, compares their sizes, about 4.9 MB against under 10 KB, and checks which one loads an external script. Reopening both files in a browser with the network disabled confirms the difference in practice.

### Exercise 4: answer contract

**Learner contract:** **Tracing:** Trace one row into x, y, color, and hover fields and explain what the reader can infer from each visible encoding. **Progressive hint:** A field retained only in source data is not visibly encoded. **Verify:** For one known row, assert its x/y values, visible group, and bounded hover fields; explain one source field intentionally not encoded.

**Reasoning:** Each visible channel answers a different question: x and y positions give the bill and tip of each point, color tells which meal it belongs to, and the hover box shows the fields named in its template on demand. The shared implementation for Exercises 3-4 finds the second row in the Dinner trace at the expected x and y values and checks the hover template. `table_id` exists in the data but is encoded nowhere, so a reader cannot infer it from the chart; it is left out deliberately because an identifier adds no analytical meaning.

### Exercise 5: answer contract

**Learner contract:** **Implementation:** Implement a Plotly scatter builder that validates required columns, bounds hover fields, and returns a figure without writing files. **Progressive hint:** Separate figure construction from export. **Verify:** Test valid data and missing-column data; assert the valid builder returns a figure with expected traces while the invalid path lists exact missing names and writes nothing.

**Reasoning:** Validating the required columns before calling Plotly turns a deep library error into one message that lists every missing name, and returning the figure without writing files keeps construction separate from export, so the builder is easy to test. Limiting hover fields to five keeps tooltips readable. The shared implementation for Exercises 5-7 asserts that a valid call returns two traces, one per meal, and that `write_html` is never called during construction.

### Exercise 6: answer contract

**Learner contract:** **Debugging:** Repair a chart-builder failure caused by a misspelled column and return an actionable error listing missing names. **Progressive hint:** Validate the schema before calling the plotting library. **Verify:** Pass two misspelled/missing fields and assert one actionable pre-plot error names both before Plotly receives the frame.

**Reasoning:** A misspelled column passed straight to Plotly fails inside the library, one name at a time, after work has started. Comparing the requested names with `frame.columns` first reports every problem at once in a stable, sorted order: `missing chart columns: bil, meals`. The shared implementation for Exercises 5-7 replaces `px.scatter` with a mock and asserts that it was never called, which proves the error happens before Plotly receives the frame.

### Exercise 7: answer contract

**Learner contract:** **Edge case and explanation:** Design deterministic sampling or aggregation for a million-row interactive chart while preserving important groups. **Progressive hint:** Browser rendering and HTML size are part of the data contract. **Verify:** Apply the deterministic reduction twice and assert identical rows/group representation, bounded payload size, and retained important-group counts.

**Reasoning:** A browser cannot draw a million points responsively, and an HTML file holding them all would be very large, so the chart needs a reduction that is deterministic and keeps the groups that matter. The `reduce_for_chart` helper ranks rows by a seeded random key within each group and keeps up to 2,000 per group, so a rare group with about a thousand rows keeps every row instead of being sampled away. The shared implementation for Exercises 5-7 runs it twice and gets identical rows, prints the original and displayed row counts, and checks that the figure's JSON stays small.

## Expanded mastery lab solutions

Use interaction to answer a question, not to decorate a chart. Keep tooltips, filters, payload size, and offline HTML behavior intentional.

### Shared implementation for Exercises 3-4: Portability and visible encodings

Embedded Plotly JavaScript makes a larger standalone file that works offline;
a CDN-based file is smaller but needs network access. A reader can interpret
only fields encoded on axes, color/shape, facets, labels, or tooltips.

```python
import re
from pathlib import Path

import pandas as pd
import plotly.express as px

points = pd.DataFrame(
    {
        "bill": [10.0, 20.0, 30.0],
        "tip": [1.0, 4.0, 5.0],
        "meal": ["Lunch", "Dinner", "Dinner"],
        "table_id": ["t1", "t2", "t3"],
    }
)
chart = px.scatter(points, x="bill", y="tip", color="meal", hover_data=["meal"])

export_dir = Path("artifacts/day26")
export_dir.mkdir(parents=True, exist_ok=True)
embedded = export_dir / "scatter-embedded.html"
cdn = export_dir / "scatter-cdn.html"
chart.write_html(embedded, include_plotlyjs=True)
chart.write_html(cdn, include_plotlyjs="cdn")
external_script = re.compile(r"<script[^>]+src=['\"]https?://", flags=re.IGNORECASE)
print({path.name: path.stat().st_size for path in (embedded, cdn)})
assert external_script.search(embedded.read_text(encoding="utf-8")) is None
assert external_script.search(cdn.read_text(encoding="utf-8")) is not None
assert embedded.stat().st_size > 100 * cdn.stat().st_size

row = points.iloc[1]
dinner = next(trace for trace in chart.data if trace.name == "Dinner")  # color group
position = list(dinner.x).index(row["bill"])  # x encodes bill
assert dinner.y[position] == row["tip"]  # y encodes tip
assert "meal=" in dinner.hovertemplate  # meal is shown on hover
assert "table_id" not in dinner.hovertemplate  # kept in the data, not encoded
```

### Shared implementation for Exercises 5-7: Validate before rendering

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


from unittest import mock

sample = pd.DataFrame({"bill": [10, 20, 30], "tip": [1, 4, 5], "meal": ["L", "D", "D"]})
with mock.patch.object(Figure, "write_html") as fake_write:
    figure = build_scatter(sample, x="bill", y="tip", color="meal", hover=["meal"])
fake_write.assert_not_called()  # construction does no I/O
assert len(figure.data) == 2

with mock.patch.object(px, "scatter") as fake_scatter:
    try:
        build_scatter(sample, x="bil", y="tip", color="meals")
    except ValueError as error:
        message = str(error)
    else:
        raise AssertionError("misspelled columns should fail before plotting")
fake_scatter.assert_not_called()  # Plotly never received the frame
assert message == "missing chart columns: bil, meals"

# Deterministic reduction that keeps a rare group intact.
import numpy as np

rng = np.random.default_rng(26)
large = pd.DataFrame(
    {
        "group": np.where(rng.random(1_000_000) < 0.001, "rare", "common"),
        "value": rng.normal(size=1_000_000),
    }
)


def reduce_for_chart(frame: pd.DataFrame, *, per_group: int, seed: int) -> pd.DataFrame:
    """Keep up to per_group rows from every group, chosen by a seeded key."""
    keys = pd.Series(np.random.default_rng(seed).random(len(frame)), index=frame.index)
    rank = keys.groupby(frame["group"]).rank(method="first")
    return frame.loc[rank <= per_group]


first = reduce_for_chart(large, per_group=2_000, seed=7)
pd.testing.assert_frame_equal(first, reduce_for_chart(large, per_group=2_000, seed=7))
counts = first["group"].value_counts()
assert counts["common"] == 2_000
assert counts["rare"] == (large["group"] == "rare").sum()  # every rare row kept
print({"original_rows": len(large), "displayed_rows": len(first)})
payload = len(px.scatter(first, x=first.index, y="value", color="group").to_json())
assert payload < 1_000_000  # bounded HTML payload
```

For very large data, use a fixed-seed stratified sample by important groups or
aggregate to meaningful bins. Report the original and displayed row counts.
When exporting for offline use, choose an embedded-JavaScript mode deliberately
and test the file with networking disabled.
