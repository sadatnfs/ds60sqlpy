# Day 25 — Visualization with Matplotlib and Seaborn

**Level:** Intermediate

A chart is an encoding of data into position, color, shape, and size. Choose the
encoding for the question, then make the figure legible and reproducible.

## Learning objectives

By the end of this lesson, you can:

- choose a distribution, comparison, relationship, or trend chart;
- use Matplotlib's figure/axes object model;
- add informative titles, labels, units, legends, and accessible colors;
- apply one consistent Seaborn theme;
- export deterministic figures at an appropriate size and resolution.

## Prerequisites

Complete Day 24 (`python-24`): EDA questions, distributions, segmentation, and
data-quality caveats.





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

2. Read `python/ds-60day/companion-guides/day25_viz_matplotlib_seaborn.md`, then open `python/ds-60day/notebooks/day25_viz_matplotlib_seaborn.ipynb` from the repository
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

**Lesson outcome:** use day 25 — visualization with matplotlib and seaborn to practice static chart choice, figure/axes ownership, labeling, and reproducible export
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

A visualization maps data fields to visual encodings such as position,
length, color, shape, or size. Choose a chart from the analytical
question and variable types: bars compare categories, histograms show a
numeric distribution, lines emphasize ordered/time trends, and scatter
plots show relationships between two numeric variables.

Matplotlib separates a **Figure** (the full canvas) from one or more
**Axes** (plot regions). Prefer the object-oriented API:
`fig, ax = plt.subplots()`, plot onto `ax`, label the axes, then save
through `fig`. State units and denominators, use ordering intentionally,
and never encode meaning through color alone.

### Vocabulary in plain language

- **mark:** a visible graphical element such as a point, line, or bar.
- **encoding:** the mapping from a data field to a visual property.
- **Figure:** the complete Matplotlib canvas.
- **Axes:** one plotting region with scales, labels, and marks.
- **distribution:** the frequency and shape of a variable's values.
- **accessibility:** design that remains interpretable across vision and interaction needs.

### Syntax anatomy

`fig, ax = plt.subplots()` creates and returns both ownership objects.
`ax.hist(values, bins=...)` adds marks to the axes; `ax.set(...)` sets
title and labels; `fig.tight_layout()` adjusts spacing; and
`fig.savefig(path, dpi=..., bbox_inches="tight")` serializes the canvas.
Save before closing the figure.

### Worked example 1 — Build a labeled distribution plot

Constructed data keeps the lesson offline and deterministic. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
import matplotlib.pyplot as plt

durations = [2, 3, 3, 4, 5, 8, 13]
fig, ax = plt.subplots(figsize=(5, 3))
ax.hist(durations, bins=[0, 3, 6, 9, 12, 15], edgecolor="black")
ax.set(title="Task duration distribution", xlabel="Duration (minutes)", ylabel="Tasks")
fig.tight_layout()
(type(fig).__name__, type(ax).__name__, len(ax.patches))
```

**Expected observation**

```text
The tuple identifies `Figure`, `Axes`, and five histogram bins. The displayed chart has units on both axes.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Make category ordering explicit

Bar positions should reflect the intended comparison, not accidental input order. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
categories = ["bronze", "silver", "gold"]
counts = [8, 5, 2]
fig2, ax2 = plt.subplots(figsize=(5, 3))
bars = ax2.bar(categories, counts, color=["0.45", "0.65", "0.85"])
ax2.set(title="Accounts by tier", xlabel="Tier", ylabel="Accounts")
ax2.bar_label(bars)
fig2.tight_layout()
[bar.get_height() for bar in bars]
```

**Expected observation**

```text
`[8, 5, 2]`. Direct value labels make the quantities readable without relying on color.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Write the question, audience, field types, units, and denominator before choosing a chart.
2. Keep figure/axes references and add labels through the axes object.
3. Inspect skew, missing groups, and category order rather than accepting plotting defaults.
4. Create the output directory and save through the figure before display/close; reopen the file to verify it is nonblank.

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

**Useful alternative:** Seaborn offers statistical defaults on top of Matplotlib; use the returned axes and retain explicit labeling/export control.

**Boundary to remember:** Long labels, zero/missing groups, extreme skew, overlapping points, color-vision differences, and tiny figures require adaptation.
<!-- END BEGINNER DEEP DIVE -->

## Vocabulary and mental model

- **Figure:** entire output canvas; **Axes:** one plotting area within it.
- **Mark:** geometric object such as a point, line, or bar.
- **Encoding:** mapping from a data field to position, color, or another visual
  property.
- **Scale:** mapping from data values to visual range.
- **Overplotting:** marks overlap enough to hide density.
- **Resolution:** pixel density for raster output such as PNG.

## Worked example

```python
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

data = pd.DataFrame({"group": ["A", "A", "B", "B"], "value": [2, 4, 3, 7]})
sns.set_theme(style="whitegrid")

fig, ax = plt.subplots(figsize=(6, 4))
sns.boxplot(data=data, x="group", y="value", ax=ax)
ax.set(title="Value distribution by group", xlabel="Group", ylabel="Value")
fig.tight_layout()

output = Path("artifacts") / "boxplot.png"
output.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(output, dpi=150)
plt.close(fig)
```

The example is offline. Closing completed figures matters in loops and long
notebook sessions.

## Dataset note

The notebook uses Seaborn's `tips` sample. First uncached use downloads it; later
runs use Seaborn's cache. Prime the cache while online or substitute a
constructed/local frame.

## Exercises and progressive hints

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Recreate two Day 24 plots and improve their communication. **For each:** write the question and reader, choose the mark/encoding, label units and denominator, order categories deliberately, and add accessible non-color cues where needed.
   **Expected behavior:** a reader can state the intended comparison without reading surrounding code.
   **Verify:** reconcile plotted counts/summary values to the source DataFrame.

2. Export both figures under an ignored learner artifact directory with consistent dimensions, style, filename, and resolution. **Constraints:** use `Path`, create parents, call `fig.tight_layout()`, and save through the figure before display/close.
   **Verify:** files exist, are nonempty, reopen successfully, and contain the expected title/axes rather than a blank canvas.

### Additional mastery practice

Choose a chart from the question and data types, then make units, denominators, ordering, uncertainty, and accessibility explicit.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Choose among bar, histogram, line, and scatter plots for category comparison, distribution, time trend, and two-number relationship.
   **Progressive hint:** Match the mark and axes to the analytical question.
   **Verify:** Create a question-to-chart table and assert each of the four questions maps to the intended mark and axis variable types with a one-sentence reason.
4. **Tracing:** Trace figure and axes ownership when using `fig, ax = plt.subplots()` and explain where title, labels, and save operations belong.
   **Progressive hint:** The figure owns the canvas; the axes owns one plot region.
   **Verify:** Assert the title/x/y labels live on `ax`, the canvas saves through `fig`, and the expected number of axes/marks exists.
5. **Implementation:** Implement a reusable distribution function accepting an axes object, units, and title without calling `show`.
   **Progressive hint:** Returning the axes makes composition and testing easier.
   **Verify:** Call the function on a supplied axes, assert it returns that same axes, labels/units are set, expected marks exist, and no global `show` is called.
6. **Debugging:** Repair an export that calls `show()` or closes the figure before `savefig`, producing a blank file in some environments.
   **Progressive hint:** Save through the figure before display/close.
   **Verify:** Save before close and assert the output file is nonempty/reopenable; reproduce the old blank path once as evidence of operation order.
7. **Edge case and explanation:** Adapt a chart for long category labels, color-vision differences, missing groups, and a very skewed distribution.
   **Progressive hint:** Do not communicate meaning through color alone.
   **Verify:** Inspect a fixture containing all four challenges and assert labels are readable, groups remain distinguishable without color, and skew/missingness policy is visible.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.

## Self-check

- When should a histogram, box plot, line plot, or scatter plot be used?
- Why is a truncated bar-chart baseline potentially misleading?
- How can opacity, aggregation, or faceting address overplotting?
- What output format suits web display versus scalable print?

Expected behavior: plots have unambiguous labels/units, remain understandable
without the notebook narration, and save to predictable paths.

## Common pitfalls and diagnosis

- **Labels are clipped in the saved image:** call `tight_layout` or use
  `constrained_layout=True`.
- **A blank file is saved:** save through the intended `fig` before closing or
  clearing it.
- **Many figures consume memory:** close each completed figure.
- **Color is the only group signal:** use an accessible palette plus shape,
  line style, faceting, or direct labels where appropriate.
- **A line connects unordered categories/time:** sort the x dimension and verify
  that connecting observations is meaningful.

## Continue

- [Open the learner notebook](../notebooks/day25_viz_matplotlib_seaborn.ipynb)
- [Check the separate solution](../solutions/day25_viz_matplotlib_seaborn/day25_solutions.md)
- [Next: Day 26 — Interactive visualization](day26_viz_plotly_altair.md)

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-25`
(Day 25 — Visualization with Matplotlib and Seaborn). I am a complete beginner. Emphasize static chart choice, figure/axes ownership, labeling, and reproducible export.
Read `python/ds-60day/companion-guides/day25_viz_matplotlib_seaborn.md` and use the learner notebook
`python/ds-60day/notebooks/day25_viz_matplotlib_seaborn.ipynb`. Do not open or quote anything under `solutions/` unless
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
