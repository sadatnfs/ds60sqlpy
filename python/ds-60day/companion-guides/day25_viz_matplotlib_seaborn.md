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

1. Recreate two Day 24 plots with improved labeling. **Hint:** for each, write
   the question, intended reader, visual encoding, and required units before
   changing code.
2. Export figures to `reports/figures/` with a consistent style. **Hint:** use
   the figure object, create the directory with `Path`, call `tight_layout`, and
   save before any display/close step.

### Additional mastery practice

Choose a chart from the question and data types, then make units, denominators, ordering, uncertainty, and accessibility explicit.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Choose among bar, histogram, line, and scatter plots for category comparison, distribution, time trend, and two-number relationship.
   **Progressive hint:** Match the mark and axes to the analytical question.
4. **Tracing:** Trace figure and axes ownership when using `fig, ax = plt.subplots()` and explain where title, labels, and save operations belong.
   **Progressive hint:** The figure owns the canvas; the axes owns one plot region.
5. **Implementation:** Implement a reusable distribution function accepting an axes object, units, and title without calling `show`.
   **Progressive hint:** Returning the axes makes composition and testing easier.
6. **Debugging:** Repair an export that calls `show()` or closes the figure before `savefig`, producing a blank file in some environments.
   **Progressive hint:** Save through the figure before display/close.
7. **Edge case and explanation:** Adapt a chart for long category labels, color-vision differences, missing groups, and a very skewed distribution.
   **Progressive hint:** Do not communicate meaning through color alone.

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
