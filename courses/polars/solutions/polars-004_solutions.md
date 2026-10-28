# polars-004: explained reference

Explain how missingness changes a specific calculation.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Count valid finite values

Check is_not_null and invert is_nan with an appropriate null policy. Infinity is another category and would need an is_finite check if it is forbidden.

**Expected:** The numeric fixture has 2 such values.

## 2. Keep a missingness indicator

Create was_null from the original column before fill_null. A flag computed after filling would falsely report no missing observations.

**Expected:** The flag identifies the original absent record even after filling.

## 3. Change the denominator

The numerical difference follows from both changed values and denominator. Neither estimate is universally correct without a missing-data model.

**Expected:** Observed mean is 2.5; zero-filled mean is 1.25.

## 4. Retain unknown flags

The operation changes inclusion policy. Label unknown rows in the output so they are not described as confirmed positive observations.

**Expected:** Ids 1 and 3 remain.

## 5. Predict logical outcomes

False does not determine an OR result; true does. This reasoning is more reliable than memorizing isolated truth-table cells.

**Expected:** The answers are unknown and true.

## 6. Detect invalid arithmetic

Use finite-value checks at the transformation boundary. Filling the symptom without inspecting a zero denominator or invalid domain can hide a coding or modeling error.

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

Explain how missingness changes a specific calculation. Build a table with observed, missing and invalid values, show each inclusion policy, and state which population the resulting statistic describes. Carry that accounting into downstream feature engineering so training and serving apply the same policy.
