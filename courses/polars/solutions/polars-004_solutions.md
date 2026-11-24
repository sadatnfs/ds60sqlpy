# polars-004: explained reference

Explain how missingness changes a specific calculation.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Count valid finite values

Check is_not_null and invert is_nan with an appropriate null policy. Infinity is another category and would need an is_finite check if it is forbidden.

```python
import polars as pl

frame = pl.DataFrame({"x": [1.0, None, float("nan"), 4.0]})
observed = frame.select(pl.col("x").fill_nan(None).count()).item()
assert observed == 2
```

**Why it holds here:** Of 1.0, null, NaN and 4.0, only 1.0 and 4.0 are real observations. Converting NaN to null first lets count(), which skips nulls, return 2.

**Plausible wrong approach:** Calling count() without fill_nan returns 3, because NaN is a valid float value rather than a null.

**How to verify:** Run the answer code and assert observed == 2; frame['x'].count() alone returns 3.

**Expected:** The numeric fixture has 2 such values.

## 2. Keep a missingness indicator

Create was_null from the original column before fill_null. A flag computed after filling would falsely report no missing observations.

**Why it holds here:** The flag must be created from the original column, where the null is still present at index 1.

**Plausible wrong approach:** Computing is_null after fill_null(0) returns all False, so the record of missingness is lost.

**How to verify:** Add pl.col('x').is_null().alias('was_null') before filling and check it is [False, True, False, False].

**Expected:** The flag identifies the original absent record even after filling.

## 3. Change the denominator

The numerical difference follows from both changed values and denominator. Neither estimate is universally correct without a missing-data model.

```python
import polars as pl

frame = pl.DataFrame({"x": [1.0, None, float("nan"), 4.0]})
means = frame.select(
    pl.col("x").fill_nan(None).mean().alias("observed_mean"),
    pl.col("x").fill_nan(None).fill_null(0).mean().alias("zero_filled_mean"),
)
assert means.row(0) == (2.5, 1.25)
```

**Why it holds here:** The observed mean divides 1.0 plus 4.0 by 2, giving 2.5. Zero filling adds two zeros and divides by 4, giving 1.25.

**Plausible wrong approach:** Using fill_null(0) without fill_nan leaves NaN in place and makes the mean NaN.

**How to verify:** Run the answer code and assert means.row(0) == (2.5, 1.25).

**Expected:** Observed mean is 2.5; zero-filled mean is 1.25.

## 4. Retain unknown flags

The operation changes inclusion policy. Label unknown rows in the output so they are not described as confirmed positive observations.

**Why it holds here:** A plain filter on flag keeps only id 1, because null is not true. fill_null(True) treats the unknown row as included, so ids 1 and 3 remain.

**Plausible wrong approach:** Using fill_null(False) would drop id 3, the opposite policy.

**How to verify:** Run frame.filter(pl.col('flag').fill_null(True)) and assert ids are [1, 3].

**Expected:** Ids 1 and 3 remain.

## 5. Predict logical outcomes

False does not determine an OR result; true does. This reasoning is more reliable than memorizing isolated truth-table cells.

**Why it holds here:** With OR, true dominates; false does not. false OR unknown stays unknown, true OR unknown is true.

**Plausible wrong approach:** Treating unknown as false would wrongly give false for the first case.

**How to verify:** Check example_two: the or column is [True, None, None], with False | None giving None.

**Expected:** The answers are unknown and true.

## 6. Detect invalid arithmetic

Use finite-value checks at the transformation boundary. Filling the symptom without inspecting a zero denominator or invalid domain can hide a coding or modeling error.

**Why it holds here:** 0.0 / 0.0 yields NaN in Polars. That is a computation result, not an absent measurement.

**Plausible wrong approach:** Converting it to null and filling it later hides the zero denominator that caused it.

**How to verify:** Build pl.DataFrame({'a': [0.0], 'b': [0.0]}), compute a / b, and check is_nan() is True while is_null() is False.

**Expected:** The diagnostic identifies an arithmetic problem.

## Complete reference

```python
"""polars-004: complete bounded Polars investigation."""

import math

import polars as pl


def example_one():
    frame = pl.DataFrame({"x": [1.0, None, float("nan"), 4.0]})
    assert frame["x"].null_count() == 1
    assert frame.select(pl.col("x").is_nan().fill_null(False).sum()).item() == 1
    only_nulls = frame.with_columns(pl.col("x").fill_null(0))
    assert math.isnan(only_nulls["x"][2])
    cleaned = frame.with_columns(pl.col("x").fill_nan(None)).with_columns(pl.col("x").fill_null(0))
    assert cleaned["x"].to_list() == [1.0, 0.0, 0.0, 4.0]
    return {"missing_categories": {"null": 1, "nan": 1}, "policy_values": cleaned["x"].to_list()}


def example_two():
    frame = pl.DataFrame({"id": [1, 2, 3], "flag": [True, False, None]})
    assert frame.filter(pl.col("flag"))["id"].to_list() == [1]
    assert frame.filter(pl.col("flag").fill_null(True))["id"].to_list() == [1, 3]
    truth = pl.DataFrame({"a": [True, False, None], "b": [None, None, False]}).select(
        (pl.col("a") & pl.col("b")).alias("and"), (pl.col("a") | pl.col("b")).alias("or")
    )
    assert truth["and"].to_list() == [None, False, False]
    assert truth["or"].to_list() == [True, None, None]
    return {"filter_true": [1], "three_valued_logic": truth.to_dicts()}


def main():
    print(example_one())
    print(example_two())
    print("polars-004 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Build a table with observed, missing and invalid values, show each inclusion policy, and state which population the resulting statistic describes. Carry that accounting into downstream feature engineering so training and serving apply the same policy.
