# polars-008: Reshaping while preserving identity

## Level and prerequisites

Intermediate. Direct prerequisites: `polars-001`, `polars-003`, `polars-005`

**Outcome:** Reshape a repeated-measurement dataset with a checked compound key.

## Question and mechanism

A wide table stores repeated measurements in separate columns, while a long table stores the measurement label as a value in a column. Neither representation is inherently more correct. The useful question is which grain makes the intended operation explicit. A before/after comparison can be wide for a paired difference and long for grouped summaries or visual encodings.

Reshaping needs an identity contract. In the worked example, the pair (id, period) identifies one measurement in the long table. A pivot can reconstruct the original wide table only when that cell identity is unique, or when an explicit aggregation defines how duplicates should combine. Asking a pivot to choose an arbitrary record hides an unresolved data-model question.

Round-trip tests are useful but bounded. Reconstructing the original fixture proves preservation for those columns and values under the selected schema. It does not establish that every real-world duplicate represents an additive measurement, or that missing periods should be filled with zero. Preserve identifiers and distinguish an absent measurement from a measured zero.

## Syntax and data contract

unpivot names index columns that remain identifiers, the columns converted into long values, and the variable/value output names. pivot names the column whose values become output column names, the row identifier and the measurement column. Use select to restore a deliberate column order and sort to restore a deliberate row order before comparing tables.

## Run the lesson

Open `polars-008` in `/classroom`. Its starter `main.py` contains both worked cases, "Reshape a paired measurement table" and "Duplicate cells require a scientific decision", and prints the dictionary each case returns. The prepared `data-engineering` worker runs it in a fresh temporary directory. An `AssertionError` means that an observation differs from the case's stated contract. The inputs are small literal tables. Cases that demonstrate Parquet scans write their files into a temporary directory that is removed when the case returns. No account, network request or package download is involved. Save source and notes before switching lessons.

## Worked case 1: Reshape a paired measurement table

The first case expands two records into four (id, period) measurements, then reconstructs the original. Its comparison explicitly restores both column order and row order, avoiding an accidental reliance on a pivot display convention.

**Expected evidence:** The long table has four rows and the reconstructed wide table equals its source.

```python
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


if __name__ == "__main__":
    print(example_one())
```

## Worked case 2: Duplicate cells require a scientific decision

The second case has two measurements for the same id and period. An explicit sum produces 10, while a pivot without an aggregation rejects the ambiguity. The frequency table exposes the duplicate identity before a modeling decision is made.

**Expected evidence:** Duplicate cell frequency is 2; an explicit sum is 10; an unspecified aggregation fails.

```python
import polars as pl


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


if __name__ == "__main__":
    print(example_two())
```

## Practice

The starter contains both worked cases, so a task can change either one. Make each change in a saved copy, run it, and compare the printed result with the task's check before opening the separate explained answers.

### 1. Add a third period

Add a followup column to the wide fixture and unpivot it.

**Check:** There are six long rows for two identifiers.

**Hint:** Count identifiers times selected measurements.

### 2. Check cell identity

Count rows by id and period before pivoting.

**Check:** Each valid cell has count 1.

**Hint:** A unique row id is not enough after reshaping.

### 3. Compare sum and mean

Aggregate the duplicated values 4 and 6 using both policies.

**Check:** Sum is 10 and mean is 5.

**Hint:** Different aggregation means different questions.

### 4. Preserve missing values

Replace one measurement with null and repeat the round trip.

**Check:** The same cell remains null.

**Hint:** Missing is not zero.

### 5. Compute a paired difference

Calculate after minus before in wide form and verify from long records.

**Check:** The differences are 2 and -2.

**Hint:** Keep the id in both calculations.

### 6. Publish a grain statement

Write the row grain for both forms.

**Check:** Wide is one row per id; long is one row per id-period.

**Hint:** Column names alone do not communicate grain.

## Diagnose errors and misleading results

Unexpected duplicate errors often reveal a real ambiguity rather than a broken pivot. Diagnose the compound key before adding an aggregation. A changed total can also result from selecting the wrong measurement columns or filling absent cells. Compare counts, key sets and a few identified cells before comparing an entire printed table.

## Transfer to independent work

Demonstrate a round trip and one deliberate duplicate counterexample, then explain the chosen aggregation policy. The same reasoning applies to model comparison tables, experiment metrics and data marts.

## Primary references

- [Polars user guide: Pivots](https://docs.pola.rs/user-guide/transformations/pivot/)
- [Polars Python API reference](https://docs.pola.rs/api/python/stable/reference/index.html)

## Tutor guidance

Use the repository's `$guide-ds60sqlpy-learning` skill (`.agents/skills/guide-ds60sqlpy-learning/SKILL.md`) for `polars-008`. Inspect the learner's own source and printed output first. Ask for an explanation of unpivot, pivot, cell uniqueness, aggregation and reconciliation in their own words, then give one focused hint at a time. Keep an assertion on this synthetic fixture separate from a claim about an external dataset or deployed service.
