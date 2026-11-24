# polars-008: explained reference

Reshape a repeated-measurement dataset with a checked compound key.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Add a third period

Include followup in the on list. The expected count assumes every selected column is retained, including any explicit null values.

```python
import polars as pl

wide = pl.DataFrame({"id": [1, 2], "before": [10, 20], "after": [12, 18], "followup": [11, 19]})
long = wide.unpivot(
    index="id", on=["before", "after", "followup"], variable_name="period", value_name="value"
)
assert long.height == 6
assert long.group_by("id").len().sort("id")["len"].to_list() == [3, 3]
```

**Why it holds here:** Unpivot creates one long row for each id and listed column, so 2 ids times 3 periods gives 6 rows, with id 1 holding 10, 12, 11 and id 2 holding 20, 18, 19.

**Plausible wrong approach:** Leaving followup out of on drops its values and gives 4 rows; listing it as index would repeat it beside every period instead of making it a period.

**How to verify:** Run the answer code: long.height is 6 and the per id counts are [3, 3]. Pivot back and compare with the wide frame for a full round trip.

**Expected:** There are six long rows for two identifiers.

## 2. Check cell identity

Validate the compound key. This catches multiple records that would otherwise be compressed into one displayed cell.

**Why it holds here:** Pivot needs each (id, period) pair to identify exactly one value. A frequency table over those two keys exposes any pair with more than one row before it gets merged.

**Plausible wrong approach:** Pivoting first and inspecting the wide output only shows one number per cell, so a duplicate summed or averaged into that cell is invisible.

**How to verify:** Run long.group_by('id', 'period').len() and assert every len equals 1; for the duplicate fixture in example_two the count is 2.

**Expected:** Each valid cell has count 1.

## 3. Compare sum and mean

Choose sum for additive contributions and mean for repeated comparable measurements only when their weighting is justified. Do not infer the policy from the API.

```python
import polars as pl

duplicate = pl.DataFrame({"id": [1, 1], "period": ["after", "after"], "value": [4, 6]})
total = duplicate.pivot(on="period", index="id", values="value", aggregate_function="sum")
average = duplicate.pivot(on="period", index="id", values="value", aggregate_function="mean")
assert total["after"].item() == 10
assert average["after"].item() == 5.0
```

**Why it holds here:** The duplicate cell for id 1 holds 4 and 6. A sum treats them as two contributions and gives 10; a mean treats them as repeated readings and gives 5.0.

**Plausible wrong approach:** Omitting aggregate_function makes pivot raise ComputeError on this input, as example_two shows; guessing first or last instead just drops one reading.

**How to verify:** Run the answer code and assert total 10 and average 5.0, then decide which policy matches the meaning of value before choosing one.

**Expected:** Sum is 10 and mean is 5.

## 4. Preserve missing values

The structural operation should preserve absence. Filling nulls after the pivot is an additional analytical decision that needs explanation.

**Why it holds here:** Unpivot and pivot only move values between shapes, so a null in after for id 2 becomes a null long value and returns as a null cell.

**Plausible wrong approach:** Calling fill_null(0) during the round trip makes the rebuilt frame look complete and turns a missing measurement into a measured zero.

**How to verify:** Set id 2 after to None, unpivot, pivot back, and assert rebuilt equals the input including the null; null_count on after should still be 1.

**Expected:** The same cell remains null.

## 5. Compute a paired difference

Joining or aligning by position without the identifier can pair different people or devices. Verify identity before subtracting.

**Why it holds here:** In wide form each row already aligns before and after for one id, so after minus before gives 12 minus 10 = 2 and 18 minus 20 = -2.

**Plausible wrong approach:** Subtracting the long after rows from the long before rows by position works only while both are sorted identically; any reordering pairs one id's after with another's before.

**How to verify:** Compute the difference in wide form, then recompute from long records joined on id and assert both give [2, -2] sorted by id.

**Expected:** The differences are 2 and -2.

## 6. Publish a grain statement

Include the statement in the transformation receipt or documentation so downstream authors know which keys are valid.

**Why it holds here:** The wide frame has one row per id with one column per period; the long frame has one row per id and period. Writing that down tells consumers which columns form the key.

**Plausible wrong approach:** Describing the long table as one row per id invites a join on id alone, which fans out to 2 or 3 rows per id.

**How to verify:** Assert wide['id'].is_unique().all() and long.select('id', 'period').is_unique().all() both hold for the fixture.

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

Demonstrate a round trip and one deliberate duplicate counterexample, then explain the chosen aggregation policy. The same reasoning applies to model comparison tables, experiment metrics and data marts.
