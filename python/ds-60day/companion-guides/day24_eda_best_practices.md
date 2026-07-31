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

2. Read `python/ds-60day/companion-guides/day24_eda_best_practices.md`, then open `python/ds-60day/notebooks/day24_eda_best_practices.ipynb` from the repository
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

**Lesson outcome:** use day 24 — exploratory data analysis best practices to practice question-led exploratory data analysis with evidence, caveats, and quality checks
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

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

### Vocabulary in plain language

- **EDA:** exploratory data analysis, structured investigation before formal conclusions.
- **provenance:** where data came from and under what conditions.
- **distribution:** the pattern of values, frequency, center, spread, and shape.
- **outlier:** an observation unusually distant under a stated context.
- **association:** a measured relationship that does not itself prove causation.
- **leakage:** information unavailable at the intended decision time contaminating analysis/modeling.

### Syntax anatomy

A useful EDA paragraph follows **question → method → observation →
limitation → next check**. `frame.describe(include="all")` can orient
you but is not a conclusion. A correlation matrix measures selected
pairwise associations under assumptions; it does not explain cause,
handle every nonlinear relationship, or protect against leakage.

### Worked example 1 — Create a bounded quality profile

Make basic risks visible before plotting relationships. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

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

**Expected observation**

```text
The profile reports four rows, one duplicate row, and a 0.25 missing rate for `amount`.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Compare robust and non-robust center

One extreme value affects the mean more than the median. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
values = pd.Series([10, 11, 12, 13, 200])
{"mean": values.mean(), "median": values.median(), "max": values.max()}
```

**Expected observation**

```text
`{'mean': 49.2, 'median': 12.0, 'max': 200}`. The difference motivates inspection; it does not automatically justify deleting 200.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Write the question and row grain above the first calculation.
2. Profile missingness, duplicates, ranges, and key uniqueness before interpreting relationships.
3. Pair each finding with sample size, units, denominator, and a caveat.
4. Remove post-outcome or target-derived fields before correlation or predictive exploration.

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

**Useful alternative:** Use a compact reusable profile for orientation, then write question-specific code rather than relying on a one-click profiling report.

**Boundary to remember:** Constant/all-missing columns, tiny groups, extreme values, duplicated entities, Simpson's paradox, and time drift can invalidate naive summaries.
<!-- END BEGINNER DEEP DIVE -->

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

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Produce a concise EDA for one local or already-cached dataset, organized as question → provenance/scope/grain → quality → univariate distributions → relationships/segments → findings/caveats.
   **Expected behavior:** every table/plot answers a written question and has an observation plus limitation. **Constraint:** avoid causal language and full-data dumps.
   **Verify:** restart and reproduce all results top to bottom.

2. Add a data-quality register with one row per issue: evidence/count, possible analytical impact, proposed treatment, validation check, and status. **Coverage:** missingness, duplicates/key uniqueness, ranges, categories, and at least one dataset-specific rule.
   **Verify:** trace how each accepted treatment changes row count or a key measure and preserve rejected/unresolved issues as caveats.

### Additional mastery practice

Organize exploratory data analysis around questions, grain, quality, and evidence. Separate observed patterns from hypotheses and causal claims.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict how one extreme value can change mean, median, standard deviation, and a scatterplot.
   **Progressive hint:** Robust and non-robust summaries respond differently to outliers.
   **Verify:** Compute statistics before/after adding the extreme value; record the exact mean/median/std changes and describe the visible plot-scale effect.
4. **Tracing:** Trace row grain from transaction-level data to a customer summary and explain which questions can no longer be answered afterward.
   **Progressive hint:** Aggregation discards within-customer event detail.
   **Verify:** List questions answerable at transaction grain, then assert the customer summary row count/uniqueness and identify at least one detail that cannot be recovered.
5. **Implementation:** Implement a compact profile returning shape, duplicate count, missing rates, numeric ranges, and unique counts.
   **Progressive hint:** Bound the result rather than dumping every row/value.
   **Verify:** Run the profile on ordinary, empty, duplicate, and missing fixtures; assert bounded keys/counts/rates without embedding full data values.
6. **Debugging:** Repair an EDA that calculates correlations after target-derived fields were added and treats the strongest coefficient as causal.
   **Progressive hint:** Remove leakage and label correlations as associations.
   **Verify:** Remove the target-derived field, recompute the association, and label it noncausal; assert the leakage column cannot enter the reported matrix.
7. **Edge case and explanation:** Handle constant, all-missing, and tiny-sample columns in plots and summaries; state which results are not meaningful.
   **Progressive hint:** A calculation returning a number does not guarantee interpretability.
   **Verify:** Detect constant/all-missing/tiny columns and assert each is skipped or annotated according to policy rather than reported as an interpretable statistic.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.

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

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-24`
(Day 24 — Exploratory Data Analysis Best Practices). Direct catalog prerequisites: `python-23`.
I have completed the direct prerequisites: `python-23`. Emphasize question-led exploratory data analysis with evidence, caveats, and quality checks.
Read `python/ds-60day/companion-guides/day24_eda_best_practices.md` and use the learner notebook
`python/ds-60day/notebooks/day24_eda_best_practices.ipynb`. Do not open or quote anything under `solutions/` unless
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
