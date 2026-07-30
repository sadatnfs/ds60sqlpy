# Day 25 — Solutions: Visualization with Matplotlib & Seaborn

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

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Recreate two Day 24 plots with improved labeling. **Hint:** for each, write the question, intended reader, visual encoding, and required units before changing code.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Export figures to `reports/figures/` with a consistent style. **Hint:** use the figure object, create the directory with `Path`, call `tight_layout`, and save before any display/close step.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Prediction

**Prompt:** Choose among bar, histogram, line, and scatter plots for category comparison, distribution, time trend, and two-number relationship.

**Reasoning checkpoint:** Match the mark and axes to the analytical question. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 4 — Tracing

**Prompt:** Trace figure and axes ownership when using `fig, ax = plt.subplots()` and explain where title, labels, and save operations belong.

**Reasoning checkpoint:** The figure owns the canvas; the axes owns one plot region. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Implementation

**Prompt:** Implement a reusable distribution function accepting an axes object, units, and title without calling `show`.

**Reasoning checkpoint:** Returning the axes makes composition and testing easier. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Debugging

**Prompt:** Repair an export that calls `show()` or closes the figure before `savefig`, producing a blank file in some environments.

**Reasoning checkpoint:** Save through the figure before display/close. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Edge case and explanation

**Prompt:** Adapt a chart for long category labels, color-vision differences, missing groups, and a very skewed distribution.

**Reasoning checkpoint:** Do not communicate meaning through color alone. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

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
