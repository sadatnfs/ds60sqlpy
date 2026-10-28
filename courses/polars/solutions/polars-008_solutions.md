# polars-008: explained reference

Reshape a repeated-measurement dataset with a checked compound key.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Add a third period

Include followup in the on list. The expected count assumes every selected column is retained, including any explicit null values.

**Expected:** There are six long rows for two identifiers.

## 2. Check cell identity

Validate the compound key. This catches multiple records that would otherwise be compressed into one displayed cell.

**Expected:** Each valid cell has count 1.

## 3. Compare sum and mean

Choose sum for additive contributions and mean for repeated comparable measurements only when their weighting is justified. Do not infer the policy from the API.

**Expected:** Sum is 10 and mean is 5.

## 4. Preserve missing values

The structural operation should preserve absence. Filling nulls after the pivot is an additional analytical decision that needs explanation.

**Expected:** The same cell remains null.

## 5. Compute a paired difference

Joining or aligning by position without the identifier can pair different people or devices. Verify identity before subtracting.

**Expected:** The differences are 2 and -2.

## 6. Publish a grain statement

Include the statement in the transformation receipt or documentation so downstream authors know which keys are valid.

**Expected:** Wide is one row per id; long is one row per id-period.

## Complete reference

```python
"""polars-008: complete bounded Polars investigation."""

import polars as pl


def example_one():
    wide = pl.DataFrame({"id": [1, 2], "before": [10, 20], "after": [12, 18]})
    long = wide.unpivot(
        index="id", on=["before", "after"], variable_name="period", value_name="value"
    )
    assert long.height == 4
    rebuilt = (
        long.pivot(on="period", index="id", values="value")
        .select("id", "before", "after")
        .sort("id")
    )
    assert rebuilt.equals(wide)
    return {"long_rows": long.sort("id", "period").to_dicts(), "round_trip": True}


def example_two():
    duplicate = pl.DataFrame({"id": [1, 1], "period": ["after", "after"], "value": [4, 6]})
    result = duplicate.pivot(on="period", index="id", values="value", aggregate_function="sum")
    assert result["after"].item() == 10
    frequencies = duplicate.group_by("id", "period").len()
    assert frequencies["len"].item() == 2
    try:
        duplicate.pivot(on="period", index="id", values="value")
    except pl.exceptions.ComputeError:
        rejected = True
    else:
        rejected = False
    assert rejected
    return {"duplicate_cell_count": 2, "explicit_aggregation_total": 10}


def main():
    print(example_one())
    print(example_two())
    print("polars-008 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Reshape a repeated-measurement dataset with a checked compound key. Demonstrate a round trip and one deliberate duplicate counterexample, then explain the chosen aggregation policy. The same reasoning applies to model comparison tables, experiment metrics and data marts.
