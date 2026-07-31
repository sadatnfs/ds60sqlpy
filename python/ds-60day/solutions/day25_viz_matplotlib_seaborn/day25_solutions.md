# Day 25 — Solutions: Visualization with Matplotlib & Seaborn

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**static chart choice, figure/axes ownership, labeling, and reproducible export**.

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

### Reference pattern 1 — Build a labeled distribution plot

Constructed data keeps the lesson offline and deterministic.

```python
import matplotlib.pyplot as plt

durations = [2, 3, 3, 4, 5, 8, 13]
fig, ax = plt.subplots(figsize=(5, 3))
ax.hist(durations, bins=[0, 3, 6, 9, 12, 15], edgecolor="black")
ax.set(title="Task duration distribution", xlabel="Duration (minutes)", ylabel="Tasks")
fig.tight_layout()
(type(fig).__name__, type(ax).__name__, len(ax.patches))
```

**Expected observation:** The tuple identifies `Figure`, `Axes`, and five histogram bins. The displayed chart has units on both axes.

### Reference pattern 2 — Make category ordering explicit

Bar positions should reflect the intended comparison, not accidental input order.

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

**Expected observation:** `[8, 5, 2]`. Direct value labels make the quantities readable without relying on color.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Recreate two Day 24 plots and improve their communication. **For each:** write the question and reader, choose the mark/encoding, label units and denominator, order categories deliberately, and add accessible non-color cues where needed. **Expected behavior:** a reader can state the intended comparison without reading surrounding code. **Verify:** reconcile plotted counts/summary values to the source DataFrame.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies static chart choice, figure/axes ownership, labeling, and reproducible export.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Seaborn offers statistical defaults on top of Matplotlib; use the returned axes and retain explicit labeling/export control.

**Edge case:** Long labels, zero/missing groups, extreme skew, overlapping points, color-vision differences, and tiny figures require adaptation.

**Solution evidence to inspect:** reconcile plotted counts/summary values to the source DataFrame.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Export both figures under an ignored learner artifact directory with consistent dimensions, style, filename, and resolution. **Constraints:** use `Path`, create parents, call `fig.tight_layout()`, and save through the figure before display/close. **Verify:** files exist, are nonempty, reopen successfully, and contain the expected title/axes rather than a blank canvas.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies static chart choice, figure/axes ownership, labeling, and reproducible export.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Seaborn offers statistical defaults on top of Matplotlib; use the returned axes and retain explicit labeling/export control.

**Edge case:** Long labels, zero/missing groups, extreme skew, overlapping points, color-vision differences, and tiny figures require adaptation.

**Solution evidence to inspect:** files exist, are nonempty, reopen successfully, and contain the expected title/axes rather than a blank canvas.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Choose among bar, histogram, line, and scatter plots for category comparison, distribution, time trend, and two-number relationship. **Progressive hint:** Match the mark and axes to the analytical question. **Verify:** Create a question-to-chart table and assert each of the four questions maps to the intended mark and axis variable types with a one-sentence reason.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying static chart choice, figure/axes ownership, labeling, and reproducible export.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Seaborn offers statistical defaults on top of Matplotlib; use the returned axes and retain explicit labeling/export control.

**Edge case:** Long labels, zero/missing groups, extreme skew, overlapping points, color-vision differences, and tiny figures require adaptation.

**Solution evidence to inspect:** Create a question-to-chart table and assert each of the four questions maps to the intended mark and axis variable types with a one-sentence reason.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace figure and axes ownership when using `fig, ax = plt.subplots()` and explain where title, labels, and save operations belong. **Progressive hint:** The figure owns the canvas; the axes owns one plot region. **Verify:** Assert the title/x/y labels live on `ax`, the canvas saves through `fig`, and the expected number of axes/marks exists.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the static chart choice, figure/axes ownership, labeling, and reproducible export model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Seaborn offers statistical defaults on top of Matplotlib; use the returned axes and retain explicit labeling/export control.

**Edge case:** Long labels, zero/missing groups, extreme skew, overlapping points, color-vision differences, and tiny figures require adaptation.

**Solution evidence to inspect:** Assert the title/x/y labels live on `ax`, the canvas saves through `fig`, and the expected number of axes/marks exists.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Implement a reusable distribution function accepting an axes object, units, and title without calling `show`. **Progressive hint:** Returning the axes makes composition and testing easier. **Verify:** Call the function on a supplied axes, assert it returns that same axes, labels/units are set, expected marks exist, and no global `show` is called.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies static chart choice, figure/axes ownership, labeling, and reproducible export.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Seaborn offers statistical defaults on top of Matplotlib; use the returned axes and retain explicit labeling/export control.

**Edge case:** Long labels, zero/missing groups, extreme skew, overlapping points, color-vision differences, and tiny figures require adaptation.

**Solution evidence to inspect:** Call the function on a supplied axes, assert it returns that same axes, labels/units are set, expected marks exist, and no global `show` is called.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair an export that calls `show()` or closes the figure before `savefig`, producing a blank file in some environments. **Progressive hint:** Save through the figure before display/close. **Verify:** Save before close and assert the output file is nonempty/reopenable; reproduce the old blank path once as evidence of operation order.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in static chart choice, figure/axes ownership, labeling, and reproducible export.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Seaborn offers statistical defaults on top of Matplotlib; use the returned axes and retain explicit labeling/export control.

**Edge case:** Long labels, zero/missing groups, extreme skew, overlapping points, color-vision differences, and tiny figures require adaptation.

**Solution evidence to inspect:** Save before close and assert the output file is nonempty/reopenable; reproduce the old blank path once as evidence of operation order.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Adapt a chart for long category labels, color-vision differences, missing groups, and a very skewed distribution. **Progressive hint:** Do not communicate meaning through color alone. **Verify:** Inspect a fixture containing all four challenges and assert labels are readable, groups remain distinguishable without color, and skew/missingness policy is visible.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from static chart choice, figure/axes ownership, labeling, and reproducible export.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Seaborn offers statistical defaults on top of Matplotlib; use the returned axes and retain explicit labeling/export control.

**Edge case:** Long labels, zero/missing groups, extreme skew, overlapping points, color-vision differences, and tiny figures require adaptation.

**Solution evidence to inspect:** Inspect a fixture containing all four challenges and assert labels are readable, groups remain distinguishable without color, and skew/missingness policy is visible.
<!-- END BEGINNER SOLUTION REVIEW -->

We recreate EDA visuals with better labeling and export figures with a consistent style.

Contents
- Exercise 1: Recreate two plots with improved labeling
- Exercise 2: Export figures under the ignored course artifact directory

---

Setup
```python
import pathlib

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(context='notebook', style='whitegrid')
FIG_DIR = pathlib.Path('artifacts/day25/figures')
FIG_DIR.mkdir(parents=True, exist_ok=True)
```

Exercise 1 — Improved labeling
```python
df = sns.load_dataset('tips')

# Histogram
fig, ax = plt.subplots(figsize=(6,4))
sns.histplot(data=df, x='total_bill', kde=True, ax=ax)
ax.set(title='Distribution of Total Bill', xlabel='Total bill ($)', ylabel='Count')
fig.tight_layout(); fig.savefig(FIG_DIR/'total_bill_hist.png', dpi=150)

# Scatter with trend
fig, ax = plt.subplots(figsize=(6,4))
sns.regplot(data=df, x='total_bill', y='tip', scatter_kws={'alpha':0.4}, ax=ax)
ax.set(title='Tip vs Total Bill', xlabel='Total bill ($)', ylabel='Tip ($)')
fig.tight_layout(); fig.savefig(FIG_DIR/'tip_vs_total_bill.png', dpi=150)
```

Exercise 2 — Consistent style export
```python
plt.style.use('seaborn-v0_8-whitegrid')
for ext in ['png','pdf']:
    (FIG_DIR/'total_bill_hist').with_suffix('.'+ext)
    (FIG_DIR/'tip_vs_total_bill').with_suffix('.'+ext)
```
Notes
- Use tight_layout to avoid cut labels
- Save both PNG and PDF for web and print

---

## Expanded mastery lab solutions

Choose a chart from the question and data types, then make units, denominators, ordering, uncertainty, and accessibility explicit.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Chart choice and object ownership

Use bars for category comparisons, histograms for distributions, lines for
ordered time trends, and scatterplots for relationships between two numeric
variables. `Axes` owns labels and marks; `Figure` owns layout and saving.

### Practices 3–5 — Reusable, testable plotting

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
