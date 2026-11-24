# polars-005: explained reference

Build an aggregate whose numerator, denominator and weighting unit are explicit.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Compute a global rate

The total is not the mean of 0.1 and 0.5 because group trial counts differ. The intended weighting unit is one trial.

**Why it holds here:** Pooling adds the numerators 1, 9 and 1 to get 11 and the denominators 1, 99 and 2 to get 102, so every trial counts once and the rate is 11 / 102, about 0.108.

**Plausible wrong approach:** Averaging the two group rates 0.1 and 0.5 gives 0.3, and averaging the three row rates gives about 0.53; both let the 2 trials of group B weigh as much as the 100 trials of group A.

**How to verify:** Run frame.select(pl.col('successes').sum() / pl.col('trials').sum()).item() and compare with 11 / 102; the result should sit much closer to A's 0.1 than to B's 0.5.

**Expected:** The global rate is 11/102.

## 2. Find a zero denominator

Return null or reject it with a reason; do not silently assign rate 0, which would claim observed failures.

```python
import polars as pl

frame = pl.DataFrame(
    {"group": ["A", "A", "B", "C"], "successes": [1, 9, 1, 0], "trials": [1, 99, 2, 0]}
)
rates = (
    frame.group_by("group")
    .agg(pl.col("successes").sum(), pl.col("trials").sum())
    .with_columns(
        pl.when(pl.col("trials") > 0)
        .then(pl.col("successes") / pl.col("trials"))
        .otherwise(None)
        .alias("rate")
    )
    .sort("group")
)
# Policy: a group with no trials has an undefined rate (null), not 0 and not NaN.
assert rates["rate"].to_list() == [0.1, 0.5, None]
```

**Why it holds here:** Group C has 0 successes over 0 trials, so its rate has no defined value. The when guard on trials > 0 returns null for C while A and B keep 0.1 and 0.5.

**Plausible wrong approach:** Dividing 0 by 0 directly produces NaN, and replacing that with 0 reports a group that never ran as one that failed every trial.

**How to verify:** Run the answer code and assert rates['rate'].to_list() == [0.1, 0.5, None]; also confirm C still has trials equal to 0 in the output so a reader can see why.

**Expected:** The output follows an explicit undefined-rate policy.

## 3. Change the estimand

If the target is a uniformly sampled group, averaging group rates can be appropriate. It is not the same target as a uniformly sampled trial.

**Why it holds here:** An equal-group average answers what a randomly chosen group looks like, so (0.1 + 0.5) / 2 = 0.3 is the right number when each group, not each trial, is the sampling unit.

**Plausible wrong approach:** Reporting 0.3 as the overall success rate of trials mixes estimands; the trial-weighted answer for the same data is 11 / 102.

**How to verify:** Write both numbers next to each other with their weighting stated, and check the group average changes when a group is added while the trial-weighted rate changes in proportion to its trials.

**Expected:** The answer defines equal weighting of groups.

## 4. Audit row grain

Publish the keys and aggregation definitions. Carrying an arbitrary order_id after grouping would incorrectly imply an order-level result.

**Why it holds here:** group_by collapses the three rate rows into one row per distinct group, A and B, so the output height is 2 and each row now describes a group rather than a source record.

**Plausible wrong approach:** Taking pl.col('order_id').first() into the aggregate gives the grouped row an order label it does not represent, inviting a later join at the wrong grain.

**How to verify:** Compare frame.height (3) with the grouped height (2), and assert the grouped group column is unique.

**Expected:** Three input rows reduce to 2 groups.

## 5. Report precision inputs

The counts support interval calculations and comparisons of evidence. Equal percentages from 1 trial and 1,000 trials do not have equal uncertainty.

**Why it holds here:** Summing successes and trials inside the aggregation keeps A at 10 over 100 and B at 1 over 2, so a reader can see B's 0.5 rests on two trials.

**Plausible wrong approach:** Publishing only rate discards the counts, and nothing in 0.5 alone tells you whether it came from 2 trials or 2,000.

**How to verify:** Check the grouped output has columns group, successes, trials and rate, and that successes / trials reproduces rate on each row.

**Expected:** Both components are recoverable.

## 6. Handle an all-null group

Retaining it with a null mean makes coverage explicit. Dropping it changes the population of reported groups and should be reported.

**Why it holds here:** In example_two, group B's only value is null, so its rows count is 1, its observed count is 0 and its mean is null. Keeping the row shows that B was measured but produced nothing usable.

**Plausible wrong approach:** Filtering out B before grouping makes the summary look complete and silently shrinks the set of reported groups from two to one.

**How to verify:** Assert B's row shows rows 1, observed 0 and mean None, while A shows rows 2, observed 1 and mean 2.0.

**Expected:** Its observed count remains 0.

## Complete reference

```python
"""polars-005: complete bounded Polars investigation."""

import polars as pl


def example_one():
    frame = pl.DataFrame({"group": ["A", "A", "B"], "successes": [1, 9, 1], "trials": [1, 99, 2]})
    output = (
        frame.group_by("group")
        .agg(
            pl.col("successes").sum().alias("successes"),
            pl.col("trials").sum().alias("trials"),
            pl.len().alias("rows"),
        )
        .with_columns((pl.col("successes") / pl.col("trials")).alias("rate"))
        .sort("group")
    )
    assert output["rate"].to_list() == [0.1, 0.5]
    naive = (
        frame.filter(pl.col("group") == "A")
        .select((pl.col("successes") / pl.col("trials")).mean())
        .item()
    )
    assert abs(naive - 0.1) > 0.4
    return {"weighted_rates": output.to_dicts(), "wrong_equal_row_mean": naive}


def example_two():
    frame = pl.DataFrame({"group": ["A", "A", "B"], "value": [2, None, None]})
    result = (
        frame.group_by("group")
        .agg(
            pl.len().alias("rows"),
            pl.col("value").count().alias("observed"),
            pl.col("value").mean().alias("mean"),
        )
        .sort("group")
    )
    assert result["rows"].to_list() == [2, 1]
    assert result["observed"].to_list() == [1, 0]
    assert result["mean"].to_list() == [2.0, None]
    return {"grain": "one row per group", "summary": result.to_dicts()}


def main():
    print(example_one())
    print(example_two())
    print("polars-005 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Reconcile the totals independently with Python arithmetic, retain coverage counts, and then decide whether the result supports the intended comparison. Apply the same discipline to conversion rates, average losses and model-quality dashboards.
