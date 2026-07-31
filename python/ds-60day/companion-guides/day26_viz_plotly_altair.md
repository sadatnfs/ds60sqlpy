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





<!-- BEGIN HOW TO RUN -->
## How to run this lesson

Work from the repository root. The rendered HTML lesson is a readable
preview; execute the real notebook in VS Code or JupyterLab.

1. Confirm the course environment before changing it:

   ```powershell
   # Windows PowerShell
   $CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
       (Resolve-Path .\.venv\Scripts\python.exe).Path
   } else {
       (Resolve-Path .\.venv\python.exe).Path
   }
   & $CoursePython scripts\course.py doctor
   ```

   ```bash
   # macOS/Linux
   .venv/bin/python scripts/course.py doctor
   ```

2. Read `python/ds-60day/companion-guides/day26_viz_plotly_altair.md`, then open `python/ds-60day/notebooks/day26_viz_plotly_altair.ipynb` from the repository
   folder in VS Code or JupyterLab.
3. Select **Python (ds60sqlpy)**. Do not run `%pip` in the notebook. If
   an import is missing, use the doctor and the catalog dependency label
   to repair the shared environment.
4. Restart the kernel and run from the first cell downward. Before every
   example, write a prediction; after it runs, compare the actual value,
   type, shape, or side effect with the stated observation.
5. Attempt each numbered exercise in its own work cell. Use the explicit
   verification as part of the task. Keep `solutions/` closed until you
   have a tested attempt or deliberately ask for help.

**Lesson outcome:** use day 26 — interactive visualization with plotly and altair to practice interactive visual encodings, bounded interaction, and portable HTML export
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

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

### Vocabulary in plain language

- **interaction:** a reader action that changes or reveals a chart view.
- **tooltip:** details shown for a hovered/focused mark.
- **selection:** a user-controlled set of marks or values.
- **parameter:** a bounded value controlling an interactive expression.
- **CDN:** a remote network service supplying shared assets such as JavaScript.
- **self-contained HTML:** a file embedding the assets needed to work offline.

### Syntax anatomy

In Plotly Express, `x`, `y`, `color`, and `hover_data` name visible or
inspectable encodings. `fig.write_html(path, include_plotlyjs=True)`
embeds the JavaScript library for offline use; a CDN option makes a
smaller file that needs network access. In Altair, a chart combines a
mark with encoded fields whose type declarations affect scales and
aggregation.

### Worked example 1 — Build an inspectable Plotly figure

Return the figure so construction remains separate from export. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

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

**Expected observation**

```text
Two traces (one per team) and the `hours`/`tasks` axis titles are reported. The notebook also renders the interactive figure.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Inspect a self-contained HTML representation

Embedding removes a runtime dependency on a remote CDN. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
html = fig.to_html(full_html=True, include_plotlyjs=True)
{
    "starts_as_html": html.lstrip().lower().startswith("<html>"),
    "contains_figure_data": "Tasks completed versus hours" in html,
    "characters": len(html),
}
```

**Expected observation**

```text
Both Boolean checks are `True`; the file-sized string is large because Plotly JavaScript is embedded.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Validate required columns and dtypes before asking the plotting library to resolve them.
2. Trace one row through x, y, color, size, and tooltip fields and remove encodings without analytical purpose.
3. Bound hover fields and avoid embedding private or overly verbose records.
4. Open exported HTML without a network connection and inspect file size/performance.

### Practice ramp

Work through the numbered exercises in five modes rather than treating all
of them as blank-code prompts:

1. **Prediction:** state the value, type, shape, rows, or side effect before
   execution.
2. **Guided modification:** change one part of a worked example and explain
   which part of the result must change.
3. **Independent application:** implement the same idea with a new input and
   an explicit contract.
4. **Debugging and edge cases:** reproduce a failure, identify the violated
   assumption, and prove the repair at a boundary.
5. **Retrieval:** close the guide and explain the core model from memory
   before moving on.

**Useful alternative:** Use a static chart when one fixed comparison tells the story; add interaction only for a clear reader task.

**Boundary to remember:** Million-row payloads, missing fields, huge tooltips, misleading default aggregation, offline JavaScript, and inaccessible color-only groups need handling.
<!-- END BEGINNER DEEP DIVE -->

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

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Create an interactive histogram whose bin count can be changed only within sensible bounds. **Plotly route:** isolate a builder accepting `bins`; **Altair route:** bind a range input to a parameter.
   **Expected behavior:** changing bins alters aggregation without changing the underlying observations.
   **Verify:** test minimum/default/maximum settings and show the displayed total count remains the number of non-missing values.

2. Export the chart to a self-contained HTML file under an ignored learner artifact directory. **Constraints:** embed required JavaScript/data, use no remote font/analytics dependency, and document payload size.
   **Verify:** disconnect network access or use browser offline mode, reopen the file, and confirm tooltips/controls still function.

### Additional mastery practice

Use interaction to answer a question, not to decorate a chart. Keep tooltips, filters, payload size, and offline HTML behavior intentional.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict the portability difference between Plotly HTML that embeds its JavaScript and HTML that loads a CDN copy.
   **Progressive hint:** A CDN reference needs network access when opened.
   **Verify:** Export embedded and CDN versions, inspect asset references/file sizes, and confirm only the embedded version remains interactive with network disabled.
4. **Tracing:** Trace one row into x, y, color, and hover fields and explain what the reader can infer from each visible encoding.
   **Progressive hint:** A field retained only in source data is not visibly encoded.
   **Verify:** For one known row, assert its x/y values, visible group, and bounded hover fields; explain one source field intentionally not encoded.
5. **Implementation:** Implement a Plotly scatter builder that validates required columns, bounds hover fields, and returns a figure without writing files.
   **Progressive hint:** Separate figure construction from export.
   **Verify:** Test valid data and missing-column data; assert the valid builder returns a figure with expected traces while the invalid path lists exact missing names and writes nothing.
6. **Debugging:** Repair a chart-builder failure caused by a misspelled column and return an actionable error listing missing names.
   **Progressive hint:** Validate the schema before calling the plotting library.
   **Verify:** Pass two misspelled/missing fields and assert one actionable pre-plot error names both before Plotly receives the frame.
7. **Edge case and explanation:** Design deterministic sampling or aggregation for a million-row interactive chart while preserving important groups.
   **Progressive hint:** Browser rendering and HTML size are part of the data contract.
   **Verify:** Apply the deterministic reduction twice and assert identical rows/group representation, bounded payload size, and retained important-group counts.

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

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-26`
(Day 26 — Interactive Visualization with Plotly and Altair). I am a complete beginner. Emphasize interactive visual encodings, bounded interaction, and portable HTML export.
Read `python/ds-60day/companion-guides/day26_viz_plotly_altair.md` and use the learner notebook
`python/ds-60day/notebooks/day26_viz_plotly_altair.ipynb`. Do not open or quote anything under `solutions/` unless
I explicitly ask after making an honest attempt. Use these visible phases:
Explain, Predict, Attempt, Hint, Evidence, and Retrieval. First explain one
concept in plain language, then ask me to predict a small example and wait
for my attempt. Give only one progressive hint at a time. Help me run or
inspect my actual notebook evidence, adapt commands to my operating system,
and do not treat the rendered HTML preview as executable. Finish with 2-3
retrieval questions and one next step. Done when I can explain the mental
model without the guide, complete one independent exercise, and show the
prompt's verification evidence from my notebook.
```
