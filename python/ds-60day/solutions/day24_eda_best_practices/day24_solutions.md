# Day 24 — Solutions: EDA Best Practices

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **question-led exploratory data analysis with evidence, caveats, and quality checks**. Predict each named
result before comparing your attempt with its matching assertions.

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

### How to compare an answer

For this lesson's **question-led exploratory data analysis with evidence, caveats, and quality checks** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–2 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Produce a concise EDA for one local or already-cached dataset, organized as question → provenance/scope/grain → quality → univariate distributions → relationships/segments → findings/caveats. **Expected behavior:** every table/plot answers a written question and has an observation plus limitation. **Constraint:** avoid causal language and full-data dumps. **Verify:** restart and reproduce all results top to bottom.

**Reasoning:** Implement this exact contract as written: Produce a concise EDA for one local or already-cached dataset, organized as question → provenance/scope/grain → quality → univariate distributions → relationships/segments → findings/caveats. Expected behavior: every table/plot answers a written question and has an observation plus limitation. Constraint: avoid causal language and full-data dumps. Keep the prompt's named data and constraints visible in the code, then establish this specific result: restart and reproduce all results top to bottom. That connects the answer to question-led exploratory data analysis with evidence, caveats, and quality checks.

```python
import pandas as pd


def compact_profile(frame: pd.DataFrame) -> dict[str, object]:
    numeric = frame.select_dtypes("number")
    return {
        "shape": frame.shape,
        "duplicate_rows": int(frame.duplicated().sum()),
        "missing_rate": frame.isna().mean().round(3).to_dict(),
        "numeric_min": numeric.min().to_dict(),
        "numeric_max": numeric.max().to_dict(),
        "unique": frame.nunique(dropna=False).to_dict(),
    }


sample = pd.DataFrame({
    "customer": [1, 2, 2, 3, 4],
    "amount": [10.0, 20.0, 20.0, None, 200.0],
    "segment": ["new", "returning", "returning", "new", "unknown"],
})
profile = compact_profile(sample)
scope = {
    "question": "How does known amount differ by customer segment?",
    "provenance": "constructed offline Day 24 fixture",
    "grain": "one customer observation per row before duplicate review",
    "rows": len(sample),
}
amount_distribution = sample["amount"].describe()
segment_summary = (
    sample.groupby("segment", dropna=False, as_index=False)
    .agg(
        rows=("customer", "size"),
        known_amounts=("amount", "count"),
        total_amount=("amount", "sum"),
        median_amount=("amount", "median"),
    )
)
observations = [
    {
        "evidence": "1/5 rows has missing amount",
        "limitation": "the missingness cause is unknown",
    },
    {
        "evidence": "unknown segment contains one 200-unit observation",
        "limitation": "one row cannot describe a population pattern",
    },
]

assert profile["shape"] == (5, 3)
assert profile["duplicate_rows"] == 1
assert amount_distribution["count"] == 4
assert segment_summary["rows"].sum() == len(sample)
assert segment_summary["total_amount"].sum() == sample["amount"].sum()
assert all({"evidence", "limitation"} <= item.keys() for item in observations)
```

The sequence is explicit: question and provenance, row grain, quality
profile, univariate distribution, segment relationship, then bounded
observations with limitations. The 200-unit row is an observed outlier,
not proof that its segment causes higher amounts.

**Verification evidence:** restart and reproduce all results top to bottom.

### Exercise 2 — worked answer

**Learner contract:** Add a data-quality register with one row per issue: evidence/count, possible analytical impact, proposed treatment, validation check, and status. **Coverage:** missingness, duplicates/key uniqueness, ranges, categories, and at least one dataset-specific rule. **Verify:** trace how each accepted treatment changes row count or a key measure and preserve rejected/unresolved issues as caveats.

**Reasoning:** Trace the concrete values in this contract one step at a time: Add a data-quality register with one row per issue: evidence/count, possible analytical impact, proposed treatment, validation check, and status. Coverage: missingness, duplicates/key uniqueness, ranges, categories, and at least one dataset-specific rule. Record the named value, shape, label, or iterator position needed to establish: trace how each accepted treatment changes row count or a key measure and preserve rejected/unresolved issues as caveats. The trace exposes question-led exploratory data analysis with evidence, caveats, and quality checks directly.

```python
quality_issues = pd.DataFrame([
    {
        "issue": "duplicate business key",
        "evidence": 1,
        "possible_impact": "double-counted amount",
        "proposed_treatment": "remove the exact repeated row",
        "validation": "customer key uniqueness and total reconciliation",
        "status": "accepted",
    },
    {
        "issue": "missing amount",
        "evidence": int(sample["amount"].isna().sum()),
        "possible_impact": "incomplete totals",
        "proposed_treatment": "retain until source policy is known",
        "validation": "missing count remains visible",
        "status": "open",
    },
    {
        "issue": "amount range",
        "evidence": int(sample["amount"].gt(100).sum()),
        "possible_impact": "extreme values dominate totals",
        "proposed_treatment": "retain and report robust summaries",
        "validation": "median and maximum both reported",
        "status": "accepted",
    },
    {
        "issue": "unexpected category",
        "evidence": int(sample["segment"].eq("unknown").sum()),
        "possible_impact": "segment comparison is incomplete",
        "proposed_treatment": "preserve as explicit unknown",
        "validation": "unknown remains a visible group",
        "status": "open",
    },
    {
        "issue": "customer-specific nonnegative amount rule",
        "evidence": int(sample["amount"].lt(0).sum()),
        "possible_impact": "negative amount would invert totals",
        "proposed_treatment": "quarantine negatives if observed",
        "validation": "accepted known amounts are nonnegative",
        "status": "accepted",
    },
])
assert set(quality_issues.columns) == {
    "issue", "evidence", "possible_impact",
    "proposed_treatment", "validation", "status"
}

before_rows = len(sample)
before_total = sample["amount"].sum()
treated = sample.drop_duplicates(["customer"], keep="first")
treatment_impact = {
    "rows_removed": before_rows - len(treated),
    "known_amount_removed": float(before_total - treated["amount"].sum()),
}
assert treatment_impact == {
    "rows_removed": 1,
    "known_amount_removed": 20.0,
}
assert quality_issues.loc[
    quality_issues["status"].eq("open"), "issue"
].tolist() == ["missing amount", "unexpected category"]
```

Only the accepted exact-duplicate treatment changes data here, and its
row/amount impact is reconciled. Missingness and the unknown category
remain unresolved caveats instead of being silently removed.

**Verification evidence:** trace how each accepted treatment changes row count or a key measure and preserve rejected/unresolved issues as caveats.

## Exercises 3–7 — Expanded mastery answers

### Exercise 3 — answer contract

**Learner contract:** **Prediction:** Predict how one extreme value can change mean, median, standard deviation, and a scatterplot. **Progressive hint:** Robust and non-robust summaries respond differently to outliers. **Verify:** Compute statistics before/after adding the extreme value; record the exact mean/median/std changes and describe the visible plot-scale effect.

**Reasoning:** Predict this named state change before running it: Prediction: Predict how one extreme value can change mean, median, standard deviation, and a scatterplot. Progressive hint: Robust and non-robust summaries respond differently to outliers. Then compare the prediction with this proof target: Compute statistics before/after adding the extreme value; record the exact mean/median/std changes and describe the visible plot-scale effect. This makes question-led exploratory data analysis with evidence, caveats, and quality checks observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Compute statistics before/after adding the extreme value; record the exact mean/median/std changes and describe the visible plot-scale effect.

### Exercise 4 — answer contract

**Learner contract:** **Tracing:** Trace row grain from transaction-level data to a customer summary and explain which questions can no longer be answered afterward. **Progressive hint:** Aggregation discards within-customer event detail. **Verify:** List questions answerable at transaction grain, then assert the customer summary row count/uniqueness and identify at least one detail that cannot be recovered.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace row grain from transaction-level data to a customer summary and explain which questions can no longer be answered afterward. Progressive hint: Aggregation discards within-customer event detail. Record the named value, shape, label, or iterator position needed to establish: List questions answerable at transaction grain, then assert the customer summary row count/uniqueness and identify at least one detail that cannot be recovered. The trace exposes question-led exploratory data analysis with evidence, caveats, and quality checks directly.

**Evidence to locate in the grouped implementation:** List questions answerable at transaction grain, then assert the customer summary row count/uniqueness and identify at least one detail that cannot be recovered.

### Exercise 5 — answer contract

**Learner contract:** **Implementation:** Implement a compact profile returning shape, duplicate count, missing rates, numeric ranges, and unique counts. **Progressive hint:** Bound the result rather than dumping every row/value. **Verify:** Run the profile on ordinary, empty, duplicate, and missing fixtures; assert bounded keys/counts/rates without embedding full data values.

**Reasoning:** Implement this exact contract as written: Implementation: Implement a compact profile returning shape, duplicate count, missing rates, numeric ranges, and unique counts. Progressive hint: Bound the result rather than dumping every row/value. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Run the profile on ordinary, empty, duplicate, and missing fixtures; assert bounded keys/counts/rates without embedding full data values. That connects the answer to question-led exploratory data analysis with evidence, caveats, and quality checks.

**Evidence to locate in the grouped implementation:** Run the profile on ordinary, empty, duplicate, and missing fixtures; assert bounded keys/counts/rates without embedding full data values.

### Exercise 6 — answer contract

**Learner contract:** **Debugging:** Repair an EDA that calculates correlations after target-derived fields were added and treats the strongest coefficient as causal. **Progressive hint:** Remove leakage and label correlations as associations. **Verify:** Remove the target-derived field, recompute the association, and label it noncausal; assert the leakage column cannot enter the reported matrix.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair an EDA that calculates correlations after target-derived fields were added and treats the strongest coefficient as causal. Progressive hint: Remove leakage and label correlations as associations. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Remove the target-derived field, recompute the association, and label it noncausal; assert the leakage column cannot enter the reported matrix. The diagnosis depends on question-led exploratory data analysis with evidence, caveats, and quality checks.

**Evidence to locate in the grouped implementation:** Remove the target-derived field, recompute the association, and label it noncausal; assert the leakage column cannot enter the reported matrix.

### Exercise 7 — answer contract

**Learner contract:** **Edge case and explanation:** Handle constant, all-missing, and tiny-sample columns in plots and summaries; state which results are not meaningful. **Progressive hint:** A calculation returning a number does not guarantee interpretability. **Verify:** Detect constant/all-missing/tiny columns and assert each is skipped or annotated according to policy rather than reported as an interpretable statistic.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Handle constant, all-missing, and tiny-sample columns in plots and summaries; state which results are not meaningful. Progressive hint: A calculation returning a number does not guarantee interpretability. Values below, at, and above the named boundary must produce the evidence Detect constant/all-missing/tiny columns and assert each is skipped or annotated according to policy rather than reported as an interpretable statistic. Those cases show how question-led exploratory data analysis with evidence, caveats, and quality checks behaves at its edge.

**Evidence to locate in the grouped implementation:** Detect constant/all-missing/tiny columns and assert each is skipped or annotated according to policy rather than reported as an interpretable statistic.

## Expanded mastery lab solutions

Organize exploratory data analysis around questions, grain, quality, and evidence. Separate observed patterns from hypotheses and causal claims.

### Shared implementation for Exercises 3–4 — Robust summaries and grain

An extreme value can move the mean and standard deviation substantially, while
the median is usually more stable. Aggregating transactions to one row per
customer supports customer questions but loses event order and transaction
variation.

### Shared implementation for Exercises 5–7 — A bounded profile with interpretation guards

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
