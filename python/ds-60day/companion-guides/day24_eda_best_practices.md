# Day 24 — Exploratory Data Analysis Best Practices

**Level:** Intermediate

EDA is a reproducible investigation, not a gallery of plots. Begin with the
question and data grain, then record evidence, caveats, and next actions.

## Learning objectives

By the end of this lesson, you can:

- state the analytical question, unit of observation, and dataset scope;
- profile shape, dtypes, uniqueness, missingness, and duplicates;
- examine distributions and relationships by meaningful segments;
- separate observed evidence from an interpretation or hypothesis;
- document data-quality risks and a prioritized next step.

## Prerequisites

Complete Day 23 (`python-23`) and pandas cleaning/grouping through Day 22.

## Vocabulary and mental model

- **Unit of observation / grain:** what one row represents.
- **Distribution:** frequency and shape of one variable's values.
- **Segment:** meaningful subgroup used to test whether an overall pattern
  hides differences.
- **Outlier:** unusual observation requiring investigation, not automatic
  deletion.
- **Leakage:** information unavailable at prediction/decision time enters an
  analysis or model.
- **Hypothesis:** testable explanation prompted by evidence, not yet a fact.

## Worked example

```python
import pandas as pd

frame = pd.DataFrame(
    {
        "segment": ["a", "a", "b", "b"],
        "amount": [10.0, None, 8.0, 30.0],
    }
)
profile = {
    "shape": frame.shape,
    "dtypes": frame.dtypes.astype(str).to_dict(),
    "missing_rate": frame.isna().mean().to_dict(),
    "duplicates": int(frame.duplicated().sum()),
}
segment_summary = frame.groupby("segment").agg(
    rows=("amount", "size"),
    observed=("amount", "count"),
    median_amount=("amount", "median"),
)
```

The row count and non-missing count answer different questions and should both
be visible.

## Dataset note

The notebook uses Seaborn's `penguins` sample, which downloads on first uncached
use and is then cached. Constructed/local data is the fully offline route.

## Exercises and progressive hints

1. Produce a concise EDA summary with text and visuals for a chosen dataset.
   **Hint:** organize the notebook as question → scope/grain → quality →
   univariate → relationships/segments → findings/caveats, not in execution
   order alone.
2. Add a data-quality section with issues and next steps. **Hint:** for each
   issue record evidence, possible impact, proposed treatment, and how that
   treatment will be validated.

## Self-check

- What does one row represent, and can that grain change?
- Which missingness patterns vary by a meaningful segment?
- Is an apparent relationship evidence of causation?
- Which transformations would use target/future information and risk leakage?

Expected behavior: another learner can restart the notebook, reproduce the same
figures/tables, and distinguish findings from unresolved hypotheses.

## Common pitfalls and diagnosis

- **`dropna()` silently changes the population:** report rows/segments removed
  and compare before/after distributions.
- **Correlation is interpreted as causation:** identify confounders and frame
  the relationship as observational evidence.
- **Only averages are shown:** add distribution, sample size, and robust
  summaries such as median/quantiles.
- **Plots have no analytical purpose:** write the question each plot answers and
  remove redundant figures.
- **EDA leaks test/target information:** split before target-aware decisions and
  fit learned preprocessing on training data only.

## Continue

- [Open the learner notebook](../notebooks/day24_eda_best_practices.ipynb)
- [Check the separate solution](../solutions/day24_eda_best_practices/day24_solutions.md)
- [Next: Day 25 — Matplotlib and Seaborn](day25_viz_matplotlib_seaborn.md)
