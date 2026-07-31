# Day 24 — Solutions: EDA Best Practices

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**question-led exploratory data analysis with evidence, caveats, and quality checks**.

Exploratory data analysis (EDA) is a disciplined conversation with a
dataset, not a gallery of every possible chart. Start with an analytical
question, source/provenance, row grain, keys, and scope. Then inspect
data quality, individual distributions, relationships, segments, and
unusual records in an order that helps answer that question.

Separate an observation (“the median differs”) from a hypothesis (“one
segment may behave differently”) and from a causal claim, which EDA
alone normally cannot establish. Every table or chart needs a sentence
about evidence and a caveat. Missingness, duplicates, outliers, tiny
samples, and target leakage can make technically valid calculations
misleading.

### Vocabulary used in the worked answers

- **EDA:** exploratory data analysis, structured investigation before formal conclusions.
- **provenance:** where data came from and under what conditions.
- **distribution:** the pattern of values, frequency, center, spread, and shape.
- **outlier:** an observation unusually distant under a stated context.
- **association:** a measured relationship that does not itself prove causation.
- **leakage:** information unavailable at the intended decision time contaminating analysis/modeling.

### Reference pattern 1 — Create a bounded quality profile

Make basic risks visible before plotting relationships.

```python
import pandas as pd

sample = pd.DataFrame({
    "customer_id": [1, 2, 2, 3],
    "amount": [10.0, 12.0, 12.0, None],
    "segment": ["new", "returning", "returning", "new"],
})
profile = {
    "shape": sample.shape,
    "duplicate_rows": int(sample.duplicated().sum()),
    "missing_rate": sample.isna().mean().round(2).to_dict(),
    "unique": sample.nunique(dropna=False).to_dict(),
}
profile
```

**Expected observation:** The profile reports four rows, one duplicate row, and a 0.25 missing rate for `amount`.

### Reference pattern 2 — Compare robust and non-robust center

One extreme value affects the mean more than the median.

```python
values = pd.Series([10, 11, 12, 13, 200])
{"mean": values.mean(), "median": values.median(), "max": values.max()}
```

**Expected observation:** `{'mean': 49.2, 'median': 12.0, 'max': 200}`. The difference motivates inspection; it does not automatically justify deleting 200.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Produce a concise EDA for one local or already-cached dataset, organized as question → provenance/scope/grain → quality → univariate distributions → relationships/segments → findings/caveats. **Expected behavior:** every table/plot answers a written question and has an observation plus limitation. **Constraint:** avoid causal language and full-data dumps. **Verify:** restart and reproduce all results top to bottom.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies question-led exploratory data analysis with evidence, caveats, and quality checks.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use a compact reusable profile for orientation, then write question-specific code rather than relying on a one-click profiling report.

**Edge case:** Constant/all-missing columns, tiny groups, extreme values, duplicated entities, Simpson's paradox, and time drift can invalidate naive summaries.

**Solution evidence to inspect:** restart and reproduce all results top to bottom.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Add a data-quality register with one row per issue: evidence/count, possible analytical impact, proposed treatment, validation check, and status. **Coverage:** missingness, duplicates/key uniqueness, ranges, categories, and at least one dataset-specific rule. **Verify:** trace how each accepted treatment changes row count or a key measure and preserve rejected/unresolved issues as caveats.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the question-led exploratory data analysis with evidence, caveats, and quality checks model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use a compact reusable profile for orientation, then write question-specific code rather than relying on a one-click profiling report.

**Edge case:** Constant/all-missing columns, tiny groups, extreme values, duplicated entities, Simpson's paradox, and time drift can invalidate naive summaries.

**Solution evidence to inspect:** trace how each accepted treatment changes row count or a key measure and preserve rejected/unresolved issues as caveats.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Predict how one extreme value can change mean, median, standard deviation, and a scatterplot. **Progressive hint:** Robust and non-robust summaries respond differently to outliers. **Verify:** Compute statistics before/after adding the extreme value; record the exact mean/median/std changes and describe the visible plot-scale effect.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying question-led exploratory data analysis with evidence, caveats, and quality checks.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use a compact reusable profile for orientation, then write question-specific code rather than relying on a one-click profiling report.

**Edge case:** Constant/all-missing columns, tiny groups, extreme values, duplicated entities, Simpson's paradox, and time drift can invalidate naive summaries.

**Solution evidence to inspect:** Compute statistics before/after adding the extreme value; record the exact mean/median/std changes and describe the visible plot-scale effect.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace row grain from transaction-level data to a customer summary and explain which questions can no longer be answered afterward. **Progressive hint:** Aggregation discards within-customer event detail. **Verify:** List questions answerable at transaction grain, then assert the customer summary row count/uniqueness and identify at least one detail that cannot be recovered.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the question-led exploratory data analysis with evidence, caveats, and quality checks model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use a compact reusable profile for orientation, then write question-specific code rather than relying on a one-click profiling report.

**Edge case:** Constant/all-missing columns, tiny groups, extreme values, duplicated entities, Simpson's paradox, and time drift can invalidate naive summaries.

**Solution evidence to inspect:** List questions answerable at transaction grain, then assert the customer summary row count/uniqueness and identify at least one detail that cannot be recovered.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Implement a compact profile returning shape, duplicate count, missing rates, numeric ranges, and unique counts. **Progressive hint:** Bound the result rather than dumping every row/value. **Verify:** Run the profile on ordinary, empty, duplicate, and missing fixtures; assert bounded keys/counts/rates without embedding full data values.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies question-led exploratory data analysis with evidence, caveats, and quality checks.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use a compact reusable profile for orientation, then write question-specific code rather than relying on a one-click profiling report.

**Edge case:** Constant/all-missing columns, tiny groups, extreme values, duplicated entities, Simpson's paradox, and time drift can invalidate naive summaries.

**Solution evidence to inspect:** Run the profile on ordinary, empty, duplicate, and missing fixtures; assert bounded keys/counts/rates without embedding full data values.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair an EDA that calculates correlations after target-derived fields were added and treats the strongest coefficient as causal. **Progressive hint:** Remove leakage and label correlations as associations. **Verify:** Remove the target-derived field, recompute the association, and label it noncausal; assert the leakage column cannot enter the reported matrix.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in question-led exploratory data analysis with evidence, caveats, and quality checks.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use a compact reusable profile for orientation, then write question-specific code rather than relying on a one-click profiling report.

**Edge case:** Constant/all-missing columns, tiny groups, extreme values, duplicated entities, Simpson's paradox, and time drift can invalidate naive summaries.

**Solution evidence to inspect:** Remove the target-derived field, recompute the association, and label it noncausal; assert the leakage column cannot enter the reported matrix.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Handle constant, all-missing, and tiny-sample columns in plots and summaries; state which results are not meaningful. **Progressive hint:** A calculation returning a number does not guarantee interpretability. **Verify:** Detect constant/all-missing/tiny columns and assert each is skipped or annotated according to policy rather than reported as an interpretable statistic.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from question-led exploratory data analysis with evidence, caveats, and quality checks.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use a compact reusable profile for orientation, then write question-specific code rather than relying on a one-click profiling report.

**Edge case:** Constant/all-missing columns, tiny groups, extreme values, duplicated entities, Simpson's paradox, and time drift can invalidate naive summaries.

**Solution evidence to inspect:** Detect constant/all-missing/tiny columns and assert each is skipped or annotated according to policy rather than reported as an interpretable statistic.
<!-- END BEGINNER SOLUTION REVIEW -->

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
