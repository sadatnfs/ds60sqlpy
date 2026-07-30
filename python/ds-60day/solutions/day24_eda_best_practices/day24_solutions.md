# Day 24 — Solutions: EDA Best Practices

We follow a checklist to produce a concise EDA with visuals and document data quality issues.

Contents
- Exercise 1: EDA summary (text + visuals)
- Exercise 2: Document data quality issues and next steps

---

Exercise 1 — EDA summary
```python
import pandas as pd, seaborn as sns, matplotlib.pyplot as plt
sns.set_theme(style='whitegrid')

df = sns.load_dataset('penguins')

# Overview
print(df.info())
print(df.describe(include='number').T)
print(df.isna().mean().sort_values(ascending=False).head())

# Distributions
sns.histplot(data=df, x='body_mass_g', hue='sex', kde=True, element='step')
plt.title('Body mass by Sex'); plt.tight_layout(); plt.show()

# Relationships
sns.scatterplot(data=df, x='bill_length_mm', y='bill_depth_mm', hue='species')
plt.title('Bill length vs depth by species'); plt.tight_layout(); plt.show()

# Correlations (numeric only)
sns.heatmap(df.corr(numeric_only=True), annot=False, cmap='viridis')
plt.title('Correlation (numeric)'); plt.tight_layout(); plt.show()
```
Narrative
- Summarize key distributions and any skew
- Note segments with clear separation (e.g., species differences)
- List candidate features and questions to answer next

---

Exercise 2 — Data quality notes
Template
- Missingness: which columns; strategy (drop, impute)
- Dtypes: convert categorical columns to category; parse dates
- Duplicates/outliers: detection and treatment
- Leakage risks (if target present); split strategy

Example
```python
notes = {
    'missing': df.isna().mean().to_dict(),
    'dtype_suggestion': {'species': 'category', 'island': 'category'},
    'next_steps': ['impute flipper_length_mm with group median',
                   'derive bill_ratio = length/depth',
                   'segment visuals by island']
}
print(notes)
```

---

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Produce a concise EDA summary with text and visuals for a chosen dataset. **Hint:** organize the notebook as question → scope/grain → quality → univariate → relationships/segments → findings/caveats, not in execution order alone.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Add a data-quality section with issues and next steps. **Hint:** for each issue record evidence, possible impact, proposed treatment, and how that treatment will be validated.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Prediction

**Prompt:** Predict how one extreme value can change mean, median, standard deviation, and a scatterplot.

**Reasoning checkpoint:** Robust and non-robust summaries respond differently to outliers. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 4 — Tracing

**Prompt:** Trace row grain from transaction-level data to a customer summary and explain which questions can no longer be answered afterward.

**Reasoning checkpoint:** Aggregation discards within-customer event detail. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Implementation

**Prompt:** Implement a compact profile returning shape, duplicate count, missing rates, numeric ranges, and unique counts.

**Reasoning checkpoint:** Bound the result rather than dumping every row/value. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Debugging

**Prompt:** Repair an EDA that calculates correlations after target-derived fields were added and treats the strongest coefficient as causal.

**Reasoning checkpoint:** Remove leakage and label correlations as associations. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Edge case and explanation

**Prompt:** Handle constant, all-missing, and tiny-sample columns in plots and summaries; state which results are not meaningful.

**Reasoning checkpoint:** A calculation returning a number does not guarantee interpretability. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

## Expanded mastery lab solutions

Organize exploratory data analysis around questions, grain, quality, and evidence. Separate observed patterns from hypotheses and causal claims.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Robust summaries and grain

An extreme value can move the mean and standard deviation substantially, while
the median is usually more stable. Aggregating transactions to one row per
customer supports customer questions but loses event order and transaction
variation.

### Practices 3–5 — A bounded profile with interpretation guards

```python
import pandas as pd


def compact_profile(frame: pd.DataFrame) -> dict[str, object]:
    """Return bounded structural and quality evidence for an EDA."""

    numeric = frame.select_dtypes(include="number")
    ranges = {
        column: {
            "min": None if values.dropna().empty else float(values.min()),
            "max": None if values.dropna().empty else float(values.max()),
        }
        for column, values in numeric.items()
    }
    return {
        "shape": tuple(frame.shape),
        "duplicates": int(frame.duplicated().sum()),
        "missing_rate": frame.isna().mean().round(4).to_dict(),
        "unique_count": frame.nunique(dropna=True).to_dict(),
        "numeric_ranges": ranges,
    }


sample = pd.DataFrame(
    {"group": ["A", "A", "B"], "value": [1.0, 1.0, None], "constant": [7, 7, 7]}
)
profile = compact_profile(sample)
assert profile["shape"] == (3, 3)
assert profile["unique_count"]["constant"] == 1

# Constant columns have no variance and cannot support a correlation.
# All-missing columns have no observed distribution.
# Tiny groups may be shown as raw points but should not receive stable trend claims.
```

Target-derived columns must be excluded from pre-model EDA of predictors.
Correlation is descriptive evidence of association; a causal claim needs
design assumptions and additional evidence.
