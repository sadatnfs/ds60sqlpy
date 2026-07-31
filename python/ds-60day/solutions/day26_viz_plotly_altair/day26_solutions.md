# Day 26 — Solutions: Interactive Visualization (Plotly / Altair)

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**interactive visual encodings, bounded interaction, and portable HTML export**.

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

### Reference pattern 1 — Build an inspectable Plotly figure

Return the figure so construction remains separate from export.

```python
import pandas as pd
import plotly.express as px

points = pd.DataFrame({
    "team": ["A", "A", "B", "B"],
    "hours": [2, 4, 3, 5],
    "tasks": [3, 7, 4, 9],
})
fig = px.scatter(
    points, x="hours", y="tasks", color="team",
    hover_data=["team"], title="Tasks completed versus hours"
)
(len(fig.data), fig.layout.xaxis.title.text, fig.layout.yaxis.title.text)
```

**Expected observation:** Two traces (one per team) and the `hours`/`tasks` axis titles are reported. The notebook also renders the interactive figure.

### Reference pattern 2 — Inspect a self-contained HTML representation

Embedding removes a runtime dependency on a remote CDN.

```python
html = fig.to_html(full_html=True, include_plotlyjs=True)
{
    "starts_as_html": html.lstrip().lower().startswith("<html>"),
    "contains_figure_data": "Tasks completed versus hours" in html,
    "characters": len(html),
}
```

**Expected observation:** Both Boolean checks are `True`; the file-sized string is large because Plotly JavaScript is embedded.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Create an interactive histogram whose bin count can be changed only within sensible bounds. **Plotly route:** isolate a builder accepting `bins`; **Altair route:** bind a range input to a parameter. **Expected behavior:** changing bins alters aggregation without changing the underlying observations. **Verify:** test minimum/default/maximum settings and show the displayed total count remains the number of non-missing values.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies interactive visual encodings, bounded interaction, and portable HTML export.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use a static chart when one fixed comparison tells the story; add interaction only for a clear reader task.

**Edge case:** Million-row payloads, missing fields, huge tooltips, misleading default aggregation, offline JavaScript, and inaccessible color-only groups need handling.

**Solution evidence to inspect:** test minimum/default/maximum settings and show the displayed total count remains the number of non-missing values.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Export the chart to a self-contained HTML file under an ignored learner artifact directory. **Constraints:** embed required JavaScript/data, use no remote font/analytics dependency, and document payload size. **Verify:** disconnect network access or use browser offline mode, reopen the file, and confirm tooltips/controls still function.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies interactive visual encodings, bounded interaction, and portable HTML export.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use a static chart when one fixed comparison tells the story; add interaction only for a clear reader task.

**Edge case:** Million-row payloads, missing fields, huge tooltips, misleading default aggregation, offline JavaScript, and inaccessible color-only groups need handling.

**Solution evidence to inspect:** disconnect network access or use browser offline mode, reopen the file, and confirm tooltips/controls still function.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Predict the portability difference between Plotly HTML that embeds its JavaScript and HTML that loads a CDN copy. **Progressive hint:** A CDN reference needs network access when opened. **Verify:** Export embedded and CDN versions, inspect asset references/file sizes, and confirm only the embedded version remains interactive with network disabled.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying interactive visual encodings, bounded interaction, and portable HTML export.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use a static chart when one fixed comparison tells the story; add interaction only for a clear reader task.

**Edge case:** Million-row payloads, missing fields, huge tooltips, misleading default aggregation, offline JavaScript, and inaccessible color-only groups need handling.

**Solution evidence to inspect:** Export embedded and CDN versions, inspect asset references/file sizes, and confirm only the embedded version remains interactive with network disabled.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace one row into x, y, color, and hover fields and explain what the reader can infer from each visible encoding. **Progressive hint:** A field retained only in source data is not visibly encoded. **Verify:** For one known row, assert its x/y values, visible group, and bounded hover fields; explain one source field intentionally not encoded.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the interactive visual encodings, bounded interaction, and portable HTML export model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use a static chart when one fixed comparison tells the story; add interaction only for a clear reader task.

**Edge case:** Million-row payloads, missing fields, huge tooltips, misleading default aggregation, offline JavaScript, and inaccessible color-only groups need handling.

**Solution evidence to inspect:** For one known row, assert its x/y values, visible group, and bounded hover fields; explain one source field intentionally not encoded.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Implement a Plotly scatter builder that validates required columns, bounds hover fields, and returns a figure without writing files. **Progressive hint:** Separate figure construction from export. **Verify:** Test valid data and missing-column data; assert the valid builder returns a figure with expected traces while the invalid path lists exact missing names and writes nothing.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the interactive visual encodings, bounded interaction, and portable HTML export model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use a static chart when one fixed comparison tells the story; add interaction only for a clear reader task.

**Edge case:** Million-row payloads, missing fields, huge tooltips, misleading default aggregation, offline JavaScript, and inaccessible color-only groups need handling.

**Solution evidence to inspect:** Test valid data and missing-column data; assert the valid builder returns a figure with expected traces while the invalid path lists exact missing names and writes nothing.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair a chart-builder failure caused by a misspelled column and return an actionable error listing missing names. **Progressive hint:** Validate the schema before calling the plotting library. **Verify:** Pass two misspelled/missing fields and assert one actionable pre-plot error names both before Plotly receives the frame.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in interactive visual encodings, bounded interaction, and portable HTML export.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use a static chart when one fixed comparison tells the story; add interaction only for a clear reader task.

**Edge case:** Million-row payloads, missing fields, huge tooltips, misleading default aggregation, offline JavaScript, and inaccessible color-only groups need handling.

**Solution evidence to inspect:** Pass two misspelled/missing fields and assert one actionable pre-plot error names both before Plotly receives the frame.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Design deterministic sampling or aggregation for a million-row interactive chart while preserving important groups. **Progressive hint:** Browser rendering and HTML size are part of the data contract. **Verify:** Apply the deterministic reduction twice and assert identical rows/group representation, bounded payload size, and retained important-group counts.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from interactive visual encodings, bounded interaction, and portable HTML export.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use a static chart when one fixed comparison tells the story; add interaction only for a clear reader task.

**Edge case:** Million-row payloads, missing fields, huge tooltips, misleading default aggregation, offline JavaScript, and inaccessible color-only groups need handling.

**Solution evidence to inspect:** Apply the deterministic reduction twice and assert identical rows/group representation, bounded payload size, and retained important-group counts.
<!-- END BEGINNER SOLUTION REVIEW -->

We create an interactive histogram with dynamic bins and save to HTML.

Contents
- Exercise 1: Interactive histogram with dynamic bins
- Exercise 2: Save to HTML and open in a browser

---

Plotly Express approach
```python
import plotly.express as px
import seaborn as sns
from pathlib import Path

df = sns.load_dataset('tips')
artifact_dir = Path('artifacts/day26')
artifact_dir.mkdir(parents=True, exist_ok=True)
fig = px.histogram(df, x='total_bill', nbins=40, color='time', marginal='rug',
                   title='Interactive Total Bill Histogram')
fig.update_layout(bargap=0.05)
fig.show()
fig.write_html(
    artifact_dir / 'total_bill_hist_interactive.html',
    include_plotlyjs=True,
)
```

Altair approach (requires vega)
```python
import altair as alt, pandas as pd, seaborn as sns

df = sns.load_dataset('tips')
slider = alt.binding_range(min=10, max=80, step=5, name='Bins: ')
select_bins = alt.selection_point(bind=slider, fields=['bins'], value={'bins':40})

hist = (alt.Chart(df)
  .transform_bin('binned', field='total_bill', bin={'maxbins': {'expr': 'bins'}}, as_=['lo','hi'])
  .mark_bar()
  .encode(x='lo:Q', x2='hi:Q', y='count()', color='time:N', tooltip=['count()'])
  .add_params(select_bins))

hist.properties(width=500, height=300)
```
Notes
- `include_plotlyjs=True` keeps the exported report usable offline
- Altair interactive binning shown via a bound parameter

---

## Expanded mastery lab solutions

Use interaction to answer a question, not to decorate a chart. Keep tooltips, filters, payload size, and offline HTML behavior intentional.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Portability and visible encodings

Embedded Plotly JavaScript makes a larger standalone file that works offline;
a CDN-based file is smaller but needs network access. A reader can interpret
only fields encoded on axes, color/shape, facets, labels, or tooltips.

### Practices 3–5 — Validate before rendering

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
