# Day 25 — Solutions: Visualization with Matplotlib & Seaborn

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **static chart choice, figure/axes ownership, labeling, and reproducible export**. Predict each named
result before comparing your attempt with its matching assertions.

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

### Vocabulary used in the worked answers

- **mark:** a visible graphical element such as a point, line, or bar.
- **encoding:** the mapping from a data field to a visual property.
- **Figure:** the complete Matplotlib canvas.
- **Axes:** one plotting region with scales, labels, and marks.
- **distribution:** the frequency and shape of a variable's values.
- **accessibility:** design that remains interpretable across vision and interaction needs.

### How to compare an answer

For this lesson's **static chart choice, figure/axes ownership, labeling, and reproducible export** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–2 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Recreate two Day 24 plots and improve their communication. **For each:** write the question and reader, choose the mark/encoding, label units and denominator, order categories deliberately, and add accessible non-color cues where needed. **Expected behavior:** a reader can state the intended comparison without reading surrounding code. **Verify:** reconcile plotted counts/summary values to the source DataFrame.

**Reasoning:** Implement this exact contract as written: Recreate two Day 24 plots and improve their communication. For each: write the question and reader, choose the mark/encoding, label units and denominator, order categories deliberately, and add accessible non-color cues where needed. Expected behavior: a reader can state the intended comparison without reading surrounding code. Keep the prompt's named data and constraints visible in the code, then establish this specific result: reconcile plotted counts/summary values to the source DataFrame. That connects the answer to static chart choice, figure/axes ownership, labeling, and reproducible export.

```python
import matplotlib.pyplot as plt
import pandas as pd

source = pd.DataFrame(
    {
        "duration_minutes": [2, 3, 3, 4, 5, 8],
        "segment": ["new", "new", "returning", "new", "new", "returning"],
    }
)
values = source["duration_minutes"]
category_counts = (
    source["segment"].value_counts().reindex(["new", "returning"])
)

distribution_fig, distribution_ax = plt.subplots(figsize=(5, 3))
distribution_ax.hist(values, bins=4, edgecolor="black")
distribution_ax.set(
    title="Task duration distribution",
    xlabel="Duration (minutes)",
    ylabel="Tasks (n)",
)

category_fig, category_ax = plt.subplots(figsize=(5, 3))
bars = category_ax.bar(
    category_counts.index,
    category_counts.values,
    color="0.75",
    edgecolor="black",
    hatch=["//", ".."],
)
category_ax.bar_label(bars)
category_ax.set(
    title="Tasks by account segment",
    xlabel="Account segment",
    ylabel="Tasks (n)",
)
distribution_fig.tight_layout()
category_fig.tight_layout()

histogram_total = sum(patch.get_height() for patch in distribution_ax.patches)
assert histogram_total == source["duration_minutes"].notna().sum()
assert [bar.get_height() for bar in bars] == category_counts.tolist()
```

The operations reader can now answer two written questions: “How are
task durations distributed?” and “How many tasks belong to each
segment?” Units, denominators, labels, outlines, hatches, and deliberate
category order make both comparisons readable without color alone.

**Verification evidence:** reconcile plotted counts/summary values to the source DataFrame.

### Exercise 2 — worked answer

**Learner contract:** Export both figures under an ignored learner artifact directory with consistent dimensions, style, filename, and resolution. **Constraints:** use `Path`, create parents, call `fig.tight_layout()`, and save through the figure before display/close. **Verify:** files exist, are nonempty, reopen successfully, and contain the expected title/axes rather than a blank canvas.

**Reasoning:** Implement this exact contract as written: Export both figures under an ignored learner artifact directory with consistent dimensions, style, filename, and resolution. Constraints: use `Path`, create parents, call `fig.tight_layout()`, and save through the figure before display/close. Keep the prompt's named data and constraints visible in the code, then establish this specific result: files exist, are nonempty, reopen successfully, and contain the expected title/axes rather than a blank canvas. That connects the answer to static chart choice, figure/axes ownership, labeling, and reproducible export.

```python
from pathlib import Path
from PIL import Image

artifact_dir = Path("artifacts/day25")
artifact_dir.mkdir(parents=True, exist_ok=True)
exports = [
    (
        distribution_fig,
        artifact_dir / "task-duration-distribution.png",
        "Task duration distribution",
    ),
    (
        category_fig,
        artifact_dir / "tasks-by-segment.png",
        "Tasks by account segment",
    ),
]
for figure, destination, expected_title in exports:
    figure.tight_layout()
    assert figure.axes[0].get_title() == expected_title
    figure.savefig(destination, dpi=150, bbox_inches="tight")
    assert destination.exists() and destination.stat().st_size > 0
    with Image.open(destination) as image:
        image.verify()
    plt.close(figure)
```

Both figures use the same 5-by-3-inch dimensions, 150 DPI, naming
convention, and ignored artifact directory. Titles and axes are checked
before saving; Pillow then proves each nonempty PNG can be reopened.

**Verification evidence:** files exist, are nonempty, reopen successfully, and contain the expected title/axes rather than a blank canvas.

## Exercises 3–7 — Expanded mastery answers

### Exercise 3 — answer contract

**Learner contract:** **Prediction:** Choose among bar, histogram, line, and scatter plots for category comparison, distribution, time trend, and two-number relationship. **Progressive hint:** Match the mark and axes to the analytical question. **Verify:** Create a question-to-chart table and assert each of the four questions maps to the intended mark and axis variable types with a one-sentence reason.

**Reasoning:** Predict this named state change before running it: Prediction: Choose among bar, histogram, line, and scatter plots for category comparison, distribution, time trend, and two-number relationship. Progressive hint: Match the mark and axes to the analytical question. Then compare the prediction with this proof target: Create a question-to-chart table and assert each of the four questions maps to the intended mark and axis variable types with a one-sentence reason. This makes static chart choice, figure/axes ownership, labeling, and reproducible export observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Create a question-to-chart table and assert each of the four questions maps to the intended mark and axis variable types with a one-sentence reason.

### Exercise 4 — answer contract

**Learner contract:** **Tracing:** Trace figure and axes ownership when using `fig, ax = plt.subplots()` and explain where title, labels, and save operations belong. **Progressive hint:** The figure owns the canvas; the axes owns one plot region. **Verify:** Assert the title/x/y labels live on `ax`, the canvas saves through `fig`, and the expected number of axes/marks exists.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace figure and axes ownership when using `fig, ax = plt.subplots()` and explain where title, labels, and save operations belong. Progressive hint: The figure owns the canvas; the axes owns one plot region. Record the named value, shape, label, or iterator position needed to establish: Assert the title/x/y labels live on `ax`, the canvas saves through `fig`, and the expected number of axes/marks exists. The trace exposes static chart choice, figure/axes ownership, labeling, and reproducible export directly.

**Evidence to locate in the grouped implementation:** Assert the title/x/y labels live on `ax`, the canvas saves through `fig`, and the expected number of axes/marks exists.

### Exercise 5 — answer contract

**Learner contract:** **Implementation:** Implement a reusable distribution function accepting an axes object, units, and title without calling `show`. **Progressive hint:** Returning the axes makes composition and testing easier. **Verify:** Call the function on a supplied axes, assert it returns that same axes, labels/units are set, expected marks exist, and no global `show` is called.

**Reasoning:** Implement this exact contract as written: Implementation: Implement a reusable distribution function accepting an axes object, units, and title without calling `show`. Progressive hint: Returning the axes makes composition and testing easier. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Call the function on a supplied axes, assert it returns that same axes, labels/units are set, expected marks exist, and no global `show` is called. That connects the answer to static chart choice, figure/axes ownership, labeling, and reproducible export.

**Evidence to locate in the grouped implementation:** Call the function on a supplied axes, assert it returns that same axes, labels/units are set, expected marks exist, and no global `show` is called.

### Exercise 6 — answer contract

**Learner contract:** **Debugging:** Repair an export that calls `show()` or closes the figure before `savefig`, producing a blank file in some environments. **Progressive hint:** Save through the figure before display/close. **Verify:** Save before close and assert the output file is nonempty/reopenable; reproduce the old blank path once as evidence of operation order.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair an export that calls `show()` or closes the figure before `savefig`, producing a blank file in some environments. Progressive hint: Save through the figure before display/close. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Save before close and assert the output file is nonempty/reopenable; reproduce the old blank path once as evidence of operation order. The diagnosis depends on static chart choice, figure/axes ownership, labeling, and reproducible export.

**Evidence to locate in the grouped implementation:** Save before close and assert the output file is nonempty/reopenable; reproduce the old blank path once as evidence of operation order.

### Exercise 7 — answer contract

**Learner contract:** **Edge case and explanation:** Adapt a chart for long category labels, color-vision differences, missing groups, and a very skewed distribution. **Progressive hint:** Do not communicate meaning through color alone. **Verify:** Inspect a fixture containing all four challenges and assert labels are readable, groups remain distinguishable without color, and skew/missingness policy is visible.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Adapt a chart for long category labels, color-vision differences, missing groups, and a very skewed distribution. Progressive hint: Do not communicate meaning through color alone. Values below, at, and above the named boundary must produce the evidence Inspect a fixture containing all four challenges and assert labels are readable, groups remain distinguishable without color, and skew/missingness policy is visible. Those cases show how static chart choice, figure/axes ownership, labeling, and reproducible export behaves at its edge.

**Evidence to locate in the grouped implementation:** Inspect a fixture containing all four challenges and assert labels are readable, groups remain distinguishable without color, and skew/missingness policy is visible.

## Expanded mastery lab solutions

Choose a chart from the question and data types, then make units, denominators, ordering, uncertainty, and accessibility explicit.

### Shared implementation for Exercises 3–4 — Chart choice and object ownership

Use bars for category comparisons, histograms for distributions, lines for
ordered time trends, and scatterplots for relationships between two numeric
variables. `Axes` owns labels and marks; `Figure` owns layout and saving.

### Shared implementation for Exercises 5–7 — Reusable, testable plotting

```python
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_distribution(
    values: pd.Series, *, ax: plt.Axes, title: str, units: str
) -> plt.Axes:
    """Draw a bounded histogram on caller-owned axes."""

    observed = values.dropna()
    if observed.empty:
        ax.text(0.5, 0.5, "No observed values", ha="center", va="center")
    else:
        ax.hist(observed, bins="auto", edgecolor="black")
    ax.set(title=title, xlabel=units, ylabel="Count")
    return ax


figure, axes = plt.subplots(figsize=(6, 4))
plot_distribution(
    pd.Series([1.0, 2.0, 2.0, 50.0, None]),
    ax=axes,
    title="Order amount distribution",
    units="Amount (USD)",
)
figure.tight_layout()

# Save before any show/close operation.
# destination = Path("artifacts/day25/order_amount.png")
# destination.parent.mkdir(parents=True, exist_ok=True)
# figure.savefig(destination, dpi=150, bbox_inches="tight")
plt.close(figure)
```

For long labels, use a horizontal bar chart or wrap labels. Add direct labels,
markers, or line styles so color is not the only encoding. Report missing
groups and consider a log scale or robust inset only when its interpretation is
clearly labeled.
