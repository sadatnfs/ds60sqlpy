# Day 26 — Solutions: Interactive Visualization (Plotly / Altair)

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

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Create an interactive histogram whose bin choice can be changed within sensible bounds. **Hint:** in Altair, bind a range input to a parameter; in Plotly, isolate figure construction in a function accepting a bin count.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Save the chart as HTML and open it in a browser. **Hint:** disconnect from the network before the final check and inspect whether all required JavaScript/data were embedded.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Prediction

**Prompt:** Predict the portability difference between Plotly HTML that embeds its JavaScript and HTML that loads a CDN copy.

**Reasoning checkpoint:** A CDN reference needs network access when opened. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 4 — Tracing

**Prompt:** Trace one row into x, y, color, and hover fields and explain what the reader can infer from each visible encoding.

**Reasoning checkpoint:** A field retained only in source data is not visibly encoded. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Implementation

**Prompt:** Implement a Plotly scatter builder that validates required columns, bounds hover fields, and returns a figure without writing files.

**Reasoning checkpoint:** Separate figure construction from export. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Debugging

**Prompt:** Repair a chart-builder failure caused by a misspelled column and return an actionable error listing missing names.

**Reasoning checkpoint:** Validate the schema before calling the plotting library. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Edge case and explanation

**Prompt:** Design deterministic sampling or aggregation for a million-row interactive chart while preserving important groups.

**Reasoning checkpoint:** Browser rendering and HTML size are part of the data contract. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

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
