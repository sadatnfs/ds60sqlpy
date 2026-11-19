# Day 24 Solutions: Exploratory Data Analysis Best Practices

**Offline teaching data:** The [original synthetic fixtures](../../../fixtures/README.md) replace first-run sample-data downloads. Their values are not historical or observational evidence. Keep numerical conclusions scoped to the declared teaching input.


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

## Exercises 1-2: Worked answers

### Exercise 1: worked answer

**Learner contract:** Produce a concise EDA for one local or already-cached dataset, organized as question → provenance/scope/grain → quality → univariate distributions → relationships/segments → findings/caveats. **Expected behavior:** every table/plot answers a written question and has an observation plus limitation. **Constraint:** avoid causal language and full-data dumps. **Verify:** restart and reproduce all results top to bottom.

**Reasoning:** Writing the question, provenance, and row grain first decides what every later table is for, and the compact profile shows the quality problems (one duplicate row, one missing amount) without printing the data. The segment summary uses `dropna=False`, so no group is hidden, and the reconciliation checks, rows and totals equal to the source, prove that grouping lost nothing. Each observation pairs its evidence with a limitation, because five rows, one of them an extreme value, cannot support statements about a population or about causes.

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


sample = pd.DataFrame(
    {
        "customer": [1, 2, 2, 3, 4],
        "amount": [10.0, 20.0, 20.0, None, 200.0],
        "segment": ["new", "returning", "returning", "new", "unknown"],
    }
)
profile = compact_profile(sample)
scope = {
    "question": "How does known amount differ by customer segment?",
    "provenance": "constructed offline Day 24 fixture",
    "grain": "one customer observation per row before duplicate review",
    "rows": len(sample),
}
amount_distribution = sample["amount"].describe()
segment_summary = sample.groupby("segment", dropna=False, as_index=False).agg(
    rows=("customer", "size"),
    known_amounts=("amount", "count"),
    total_amount=("amount", "sum"),
    median_amount=("amount", "median"),
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

### Exercise 2: worked answer

**Learner contract:** Add a data-quality register with one row per issue: evidence/count, possible analytical impact, proposed treatment, validation check, and status. **Coverage:** missingness, duplicates/key uniqueness, ranges, categories, and at least one dataset-specific rule. **Verify:** trace how each accepted treatment changes row count or a key measure and preserve rejected/unresolved issues as caveats.

**Reasoning:** A quality register turns each problem into a decision with evidence, impact, treatment, validation, and status, so a reviewer can see what was done and what is still open. Only the exact duplicate is treated: removing it drops one row and 20.0 of known amount, and the impact check states both numbers precisely. The missing amount and the unknown segment stay open as caveats because no source policy justifies changing them, and the nonnegative-amount rule records a check that currently finds 0 violations, which is evidence too.

```python
quality_issues = pd.DataFrame(
    [
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
    ]
)
assert set(quality_issues.columns) == {
    "issue",
    "evidence",
    "possible_impact",
    "proposed_treatment",
    "validation",
    "status",
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
assert quality_issues.loc[quality_issues["status"].eq("open"), "issue"].tolist() == [
    "missing amount",
    "unexpected category",
]
```

Only the accepted exact-duplicate treatment changes data here, and its
row/amount impact is reconciled. Missingness and the unknown category
remain unresolved caveats instead of being silently removed.

## Exercises 3-7: Expanded mastery answers

### Exercise 3: answer contract

**Learner contract:** **Prediction:** Predict how one extreme value can change mean, median, standard deviation, and a scatterplot. **Progressive hint:** Robust and non-robust summaries respond differently to outliers. **Verify:** Compute statistics before/after adding the extreme value; record the exact mean/median/std changes and describe the visible plot-scale effect.

**Reasoning:** One extreme value pulls the mean and standard deviation strongly because both use the size of every value: adding 200 to five values near 11 raises the mean by 31.5 and the standard deviation by about 76, while the median moves by only 0.5 because it depends on order, not size. On a scatterplot, the axis must stretch to 200, so the five ordinary points are squeezed into a narrow band. The shared implementation for Exercises 3-4 prints the exact changes and the ratio of the two value ranges.

### Exercise 4: answer contract

**Learner contract:** **Tracing:** Trace row grain from transaction-level data to a customer summary and explain which questions can no longer be answered afterward. **Progressive hint:** Aggregation discards within-customer event detail. **Verify:** List questions answerable at transaction grain, then assert the customer summary row count/uniqueness and identify at least one detail that cannot be recovered.

**Reasoning:** A customer summary has one row per customer, so it answers customer-level questions such as total spend or order count, but not questions about individual transactions: which order was largest, what time of day orders arrive, or in which sequence they happened. The shared implementation for Exercises 3-4 asserts that the summary keys are unique and that the totals reconcile, and shows that the timestamp no longer exists after aggregation. Keep the transaction-level data whenever later questions may need that detail.

### Exercise 5: answer contract

**Learner contract:** **Implementation:** Implement a compact profile returning shape, duplicate count, missing rates, numeric ranges, and unique counts. **Progressive hint:** Bound the result rather than dumping every row/value. **Verify:** Run the profile on ordinary, empty, duplicate, and missing fixtures; assert bounded keys/counts/rates without embedding full data values.

**Reasoning:** A profile should report structure and quality, not data: shape, duplicate count, missing rates, unique counts, and numeric ranges stay small however many rows the frame has. Guarding `min` and `max` with `values.dropna().empty` means that a column without observations reports `None` instead of `NaN`, so absence is explicit. The shared implementation for Exercises 5-7 runs the profile on ordinary, empty, duplicate, and missing fixtures and checks that each returns the same bounded set of keys.

### Exercise 6: answer contract

**Learner contract:** **Debugging:** Repair an EDA that calculates correlations after target-derived fields were added and treats the strongest coefficient as causal. **Progressive hint:** Remove leakage and label correlations as associations. **Verify:** Remove the target-derived field, recompute the association, and label it noncausal; assert the leakage column cannot enter the reported matrix.

**Reasoning:** A field computed from the target correlates with the target by construction, so it tops the correlation list without telling you anything about the predictors; the buggy analysis reports it with a coefficient of 1.0. The repair drops target-derived columns before computing associations and labels every remaining coefficient as an association, because a correlation in observational data can come from confounding or reverse causation. The shared implementation for Exercises 5-7 shows the leaked column at the top first, then asserts that it cannot enter the repaired report.

### Exercise 7: answer contract

**Learner contract:** **Edge case and explanation:** Handle constant, all-missing, and tiny-sample columns in plots and summaries; state which results are not meaningful. **Progressive hint:** A calculation returning a number does not guarantee interpretability. **Verify:** Detect constant/all-missing/tiny columns and assert each is skipped or annotated according to policy rather than reported as an interpretable statistic.

**Reasoning:** A calculation can return a number that means nothing: a constant column has no variation, so any correlation with it is undefined; an all-missing column has no distribution; and two observations cannot support a trend. The `interpretability_notes` helper in the shared implementation for Exercises 5-7 checks each column before it is summarized and returns `skip` or `annotate` according to the policy, so these cases are reported as limitations rather than as statistics.

## Expanded mastery lab solutions

Organize exploratory data analysis around questions, grain, quality, and evidence. Separate observed patterns from hypotheses and causal claims.

### Shared implementation for Exercises 3-4: Robust summaries and grain

An extreme value can move the mean and standard deviation substantially, while
the median is usually more stable. Aggregating transactions to one row per
customer supports customer questions but loses event order and transaction
variation.

```python
import pandas as pd

values = pd.Series([10.0, 12.0, 11.0, 13.0, 9.0])
with_extreme = pd.concat([values, pd.Series([200.0])], ignore_index=True)
changes = {
    name: round(float(getattr(with_extreme, name)() - getattr(values, name)()), 2)
    for name in ("mean", "median", "std")
}
print(changes)  # {'mean': 31.5, 'median': 0.5, 'std': 75.59}
assert changes["median"] < 1 < changes["mean"] < changes["std"]
range_ratio = (with_extreme.max() - with_extreme.min()) / (values.max() - values.min())
print(f"plot axis range grows {range_ratio:.1f} times")  # ordinary points get squeezed

transactions = pd.DataFrame(
    {
        "customer": ["c1", "c1", "c2"],
        "timestamp": pd.to_datetime(["2025-01-01 09:00", "2025-01-03 18:00", "2025-01-02 12:00"]),
        "amount": [20.0, 5.0, 40.0],
    }
)
per_customer = transactions.groupby("customer", as_index=False).agg(
    orders=("amount", "size"),
    total=("amount", "sum"),
)
assert per_customer["customer"].is_unique and len(per_customer) == 2
assert per_customer["total"].sum() == transactions["amount"].sum()
# c1's two orders are now one row: their times and sizes cannot be recovered.
assert "timestamp" not in per_customer.columns
```

### Shared implementation for Exercises 5-7: A bounded profile with interpretation guards

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


sample = pd.DataFrame({"group": ["A", "A", "B"], "value": [1.0, 1.0, None], "constant": [7, 7, 7]})
profile = compact_profile(sample)
assert profile["shape"] == (3, 3)
assert profile["unique_count"]["constant"] == 1

fixtures = {
    "ordinary": pd.DataFrame({"x": [1.0, 2.0]}),
    "empty": pd.DataFrame({"x": pd.Series([], dtype="float64")}),
    "duplicate": pd.DataFrame({"x": [1.0, 1.0]}),
    "missing": pd.DataFrame({"x": [None, None]}, dtype="float64"),
}
for name, fixture in fixtures.items():
    result = compact_profile(fixture)
    assert set(result) == {"shape", "duplicates", "missing_rate", "unique_count", "numeric_ranges"}
    print(name, result["shape"], result["duplicates"], result["numeric_ranges"])
assert compact_profile(fixtures["duplicate"])["duplicates"] == 1
assert compact_profile(fixtures["missing"])["numeric_ranges"]["x"] == {"min": None, "max": None}

# A target-derived column tops the correlation list by construction.
model_frame = pd.DataFrame(
    {
        "visits": [1, 3, 2, 5, 4],
        "spend": [10.0, 25.0, 18.0, 41.0, 30.0],
        "converted": [0, 1, 0, 1, 1],
    }
)
model_frame["converted_score"] = model_frame["converted"] * 100  # leakage
buggy = model_frame.corr()["converted"].drop("converted")
assert buggy.idxmax() == "converted_score" and buggy.max() == 1.0
leakage = {"converted_score"}
predictors = [column for column in model_frame.columns if column not in leakage | {"converted"}]
association = model_frame[predictors + ["converted"]].corr()["converted"].drop("converted")
assert leakage.isdisjoint(association.index)
report = {name: f"association r={value:.2f}, not causal" for name, value in association.items()}
print(report)


def interpretability_notes(frame: pd.DataFrame, *, min_rows: int = 5) -> dict[str, str]:
    """Label columns whose summaries would not be meaningful."""
    notes = {}
    for column, values in frame.items():
        observed = values.dropna()
        if observed.empty:
            notes[column] = "skip: all values missing"
        elif observed.nunique() == 1:
            notes[column] = "skip: constant, no variation"
        elif len(observed) < min_rows:
            notes[column] = f"annotate: only {len(observed)} observations"
        else:
            notes[column] = "ok"
    return notes


guards = pd.DataFrame(
    {"constant": [7, 7, 7], "empty": [None, None, None], "tiny": [1.0, 2.0, None]},
    dtype="float64",
)
assert interpretability_notes(guards) == {
    "constant": "skip: constant, no variation",
    "empty": "skip: all values missing",
    "tiny": "annotate: only 2 observations",
}
```

Target-derived columns must be excluded from pre-model EDA of predictors.
Correlation is descriptive evidence of association; a causal claim needs
design assumptions and additional evidence.
