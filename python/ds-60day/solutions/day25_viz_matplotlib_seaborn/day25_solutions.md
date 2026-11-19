# Day 25 Solutions: Visualization with Matplotlib and seaborn

**Offline teaching data:** The [original synthetic fixtures](../../../fixtures/README.md) replace first-run sample-data downloads. Their values are not historical or observational evidence. Keep numerical conclusions scoped to the declared teaching input.


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

## Exercises 1-2: Worked answers

### Exercise 1: worked answer

**Learner contract:** Recreate two Day 24 plots and improve their communication. **For each:** write the question and reader, choose the mark/encoding, label units and denominator, order categories deliberately, and add accessible non-color cues where needed. **Expected behavior:** a reader can state the intended comparison without reading surrounding code. **Verify:** reconcile plotted counts/summary values to the source DataFrame.

**Reasoning:** Each chart starts from a written question and a reader, which decides the mark: a histogram for the distribution of durations and a bar chart for counts per segment. Labels name the units and the denominator (`Tasks (n)`), the categories are placed in a deliberate order with `reindex`, and outlines plus hatches keep the two bars distinguishable without relying on color, so the chart still works in grayscale or for readers with color-vision differences. The reconciliation compares what was drawn with the data: the histogram bar heights add up to the six non-missing durations, and the bar heights equal the category counts.

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
category_counts = source["segment"].value_counts().reindex(["new", "returning"])

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

### Exercise 2: worked answer

**Learner contract:** Export both figures under an ignored learner artifact directory with consistent dimensions, style, filename, and resolution. **Constraints:** use `Path`, create parents, call `fig.tight_layout()`, and save through the figure before display/close. **Verify:** files exist, are nonempty, reopen successfully, and contain the expected title/axes rather than a blank canvas.

**Reasoning:** Exports are reproducible when size, resolution, file names, and location are decided once and applied to every figure: both use the 5-by-3-inch size, 150 DPI, descriptive names, and the ignored `artifacts/day25` directory. Saving through the figure object, `figure.savefig`, before closing it guarantees that the file contains that figure; the title check confirms that the right figure is being saved. Checking that the file is nonempty and reopening it with Pillow's `verify` proves that a valid PNG was written, not an empty or truncated file.

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

## Exercises 3-7: Expanded mastery answers

### Exercise 3: answer contract

**Learner contract:** **Prediction:** Choose among bar, histogram, line, and scatter plots for category comparison, distribution, time trend, and two-number relationship. **Progressive hint:** Match the mark and axes to the analytical question. **Verify:** Create a question-to-chart table and assert each of the four questions maps to the intended mark and axis variable types with a one-sentence reason.

**Reasoning:** The mark follows from the question and the variable types: bars compare a count across categories on a common baseline, a histogram shows the shape and spread of one numeric variable, a line connects ordered time points so the trend is visible, and a scatterplot shows how two numeric variables vary together. Writing the choice as a small table with one reason per row makes it reviewable, and the shared implementation for Exercises 3-4 asserts the intended mark for each of the four questions.

### Exercise 4: answer contract

**Learner contract:** **Tracing:** Trace figure and axes ownership when using `fig, ax = plt.subplots()` and explain where title, labels, and save operations belong. **Progressive hint:** The figure owns the canvas; the axes owns one plot region. **Verify:** Assert the title/x/y labels live on `ax`, the canvas saves through `fig`, and the expected number of axes/marks exists.

**Reasoning:** `plt.subplots()` returns two objects with different jobs: the `Figure` owns the whole canvas, its size, layout, and saving, and each `Axes` owns one plot region, with its marks, title, and axis labels. Setting labels through `ax.set(...)` and saving through `fig.savefig(...)` keeps each operation on its owner, which avoids pyplot's hidden "current figure" state. The shared implementation for Exercises 3-4 asserts that the figure holds exactly that one axes, that the labels live on it, that it contains one line, and that saving the figure produces nonempty bytes.

### Exercise 5: answer contract

**Learner contract:** **Implementation:** Implement a reusable distribution function accepting an axes object, units, and title without calling `show`. **Progressive hint:** Returning the axes makes composition and testing easier. **Verify:** Call the function on a supplied axes, assert it returns that same axes, labels/units are set, expected marks exist, and no global `show` is called.

**Reasoning:** Passing the axes in and returning it lets the caller decide the layout, combine the plot with others, and test it without drawing to the screen; calling `show()` inside the function would take that decision away from the caller. Dropping missing values first and drawing a message when nothing remains keeps the function from failing on empty input. The shared implementation for Exercises 5-7 calls it with `plt.show` replaced by a mock, asserts that it was never called, that the same axes came back, and that the title, units, and histogram bars exist.

### Exercise 6: answer contract

**Learner contract:** **Debugging:** Repair an export that calls `show()` or closes the figure before `savefig`, producing a blank file in some environments. **Progressive hint:** Save through the figure before display/close. **Verify:** Save before close and assert the output file is nonempty/reopenable; reproduce the old blank path once as evidence of operation order.

**Reasoning:** The blank file comes from saving through pyplot's current figure after the real one has been shown or closed: `plt.savefig` then creates a new, empty figure and saves that. Calling `savefig` on the figure object before closing it ties the file to the figure that was drawn. The shared implementation for Exercises 5-7 saves the real figure, checks that the image is not uniformly white, then reproduces the old order once and shows that it writes an all-white canvas.

### Exercise 7: answer contract

**Learner contract:** **Edge case and explanation:** Adapt a chart for long category labels, color-vision differences, missing groups, and a very skewed distribution. **Progressive hint:** Do not communicate meaning through color alone. **Verify:** Inspect a fixture containing all four challenges and assert labels are readable, groups remain distinguishable without color, and skew/missingness policy is visible.

**Reasoning:** Each challenge gets its own explicit cue: long category names go on the vertical axis of a horizontal bar chart, where they have room; hatches and direct value labels distinguish the groups without color; a group with no rows is kept in the chart with a "no rows" label instead of disappearing; and the skewed amounts use a log scale that is named in the axis label, with the count of missing values in the title. The shared implementation for Exercises 5-7 builds a fixture containing all four challenges and asserts each cue, so the chart's honesty is checked rather than assumed.

## Expanded mastery lab solutions

Choose a chart from the question and data types, then make units, denominators, ordering, uncertainty, and accessibility explicit.

### Shared implementation for Exercises 3-4: Chart choice and object ownership

Use bars for category comparisons, histograms for distributions, lines for
ordered time trends, and scatterplots for relationships between two numeric
variables. `Axes` owns labels and marks; `Figure` owns layout and saving.

```python
import io

import matplotlib.pyplot as plt
import pandas as pd

chart_choices = pd.DataFrame(
    [
        ("Which segment has more tasks?", "bar", "category x, count y", "common baseline"),
        ("How are task durations spread?", "histogram", "numeric x, count y", "shows shape"),
        ("How did daily orders change?", "line", "ordered time x, numeric y", "shows trend"),
        (
            "Do longer visits mean higher spend?",
            "scatter",
            "numeric x, numeric y",
            "one point per pair",
        ),
    ],
    columns=["question", "mark", "axes", "reason"],
)
assert chart_choices["mark"].tolist() == ["bar", "histogram", "line", "scatter"]

fig, ax = plt.subplots(figsize=(4, 3))
ax.plot([1, 2, 3], [2, 4, 3], marker="o")
ax.set(title="Daily orders", xlabel="Day", ylabel="Orders (n)")
assert fig.axes == [ax]  # the figure owns the axes
assert (ax.get_title(), ax.get_xlabel(), ax.get_ylabel()) == ("Daily orders", "Day", "Orders (n)")
assert len(ax.lines) == 1  # one line mark on this axes
buffer = io.BytesIO()
fig.savefig(buffer, format="png")  # saving is a figure operation
assert buffer.getbuffer().nbytes > 0
plt.close(fig)
```

### Shared implementation for Exercises 5-7: Reusable, testable plotting

```python
from pathlib import Path
from unittest import mock

import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image


def plot_distribution(values: pd.Series, *, ax: plt.Axes, title: str, units: str) -> plt.Axes:
    """Draw a bounded histogram on caller-owned axes."""

    observed = values.dropna()
    if observed.empty:
        ax.text(0.5, 0.5, "No observed values", ha="center", va="center")
    else:
        ax.hist(observed, bins="auto", edgecolor="black")
    ax.set(title=title, xlabel=units, ylabel="Count")
    return ax


figure, axes = plt.subplots(figsize=(6, 4))
with mock.patch.object(plt, "show") as fake_show:
    returned = plot_distribution(
        pd.Series([1.0, 2.0, 2.0, 50.0, None]),
        ax=axes,
        title="Order amount distribution",
        units="Amount (USD)",
    )
fake_show.assert_not_called()
assert returned is axes
assert (axes.get_title(), axes.get_xlabel()) == ("Order amount distribution", "Amount (USD)")
assert len(axes.patches) > 0  # histogram bars exist
figure.tight_layout()

# Save through the figure before any show/close operation.
destination = Path("artifacts/day25/order_amount.png")
destination.parent.mkdir(parents=True, exist_ok=True)
figure.savefig(destination, dpi=150, bbox_inches="tight")
plt.close(figure)
with Image.open(destination) as image:
    assert image.convert("L").getextrema()[0] < 255  # something was drawn

# The old order: close first, then save through pyplot's current figure.
plt.close("all")
blank_path = destination.with_name("order_amount_blank.png")
plt.savefig(blank_path)  # pyplot creates a new, empty current figure
plt.close("all")
with Image.open(blank_path) as image:
    assert image.convert("L").getextrema() == (255, 255)  # an all-white canvas

# Long labels, no color dependence, a missing group, and a skewed distribution.
expected_groups = [
    "Enterprise accounts with annual contracts",
    "Small business monthly plans",
    "Education and nonprofit discount tier",
]
observed_counts = pd.Series(
    {"Enterprise accounts with annual contracts": 120, "Small business monthly plans": 45}
)
counts = observed_counts.reindex(expected_groups, fill_value=0)
amounts = pd.Series([1.0, 2.0, 2.0, 3.0, 5.0, 8.0, 500.0, None])

fig, (bar_ax, hist_ax) = plt.subplots(1, 2, figsize=(11, 4))
bars = bar_ax.barh(
    counts.index, counts.to_numpy(), color="0.75", edgecolor="black", hatch=["//", "..", "xx"]
)
bar_ax.bar_label(bars, labels=[str(count) if count else "no rows" for count in counts])
bar_ax.invert_yaxis()
bar_ax.set(title="Accounts by plan", xlabel="Accounts (n)")
observed = amounts.dropna()
hist_ax.hist(observed, bins=[10 ** (step / 2) for step in range(7)], edgecolor="black")
hist_ax.set_xscale("log")
hist_ax.set(
    title=f"Order amounts (n={len(observed)}, {int(amounts.isna().sum())} missing)",
    xlabel="Amount (USD, log scale)",
    ylabel="Orders (n)",
)
fig.tight_layout()
fig.canvas.draw()
assert [label.get_text() for label in bar_ax.get_yticklabels()] == expected_groups
assert len({bar.get_hatch() for bar in bars}) == 3  # distinguishable without color
assert "no rows" in [text.get_text() for text in bar_ax.texts]  # missing group visible
assert hist_ax.get_xscale() == "log" and "log scale" in hist_ax.get_xlabel()
plt.close(fig)
```

For long labels, use a horizontal bar chart or wrap labels. Add direct labels,
markers, or line styles so color is not the only encoding. Report missing
groups and consider a log scale or robust inset only when its interpretation is
clearly labeled.
