# polars-004: Null, NaN and three-valued logic

## Level and prerequisites

Beginner. Direct prerequisites: `polars-001`, `polars-003`

**Outcome:** Explain how missingness changes a specific calculation.

## Question and mechanism

A null means a value is absent under the column's validity representation. NaN is a floating-point value used for undefined or invalid arithmetic. These categories can appear together and require different checks. Counting nulls does not count NaNs, and filling nulls does not repair a NaN. Decide whether each category represents missing observation, invalid measurement or a computational failure before replacing it.

Boolean expressions introduce another important distinction. A predicate can be true, false or unknown because one of its inputs is null. A filter retains rows where its predicate is true. Unknown rows therefore disappear unless the policy explicitly treats them otherwise. That behavior is often desirable, but it must not be mistaken for proof that all retained rows came from a complete population.

Imputation is a modeling decision. Replacing missing measurements with zero changes the distribution and may change a group comparison, model score or denominator. The example uses zero only as a clearly declared teaching policy. In real work, preserve a missingness indicator and consider whether missingness itself depends on the outcome, treatment, source system or time.

## Syntax and data contract

is_null and is_nan answer different questions. is_nan can itself return null for an absent input, so fill_null(False) is appropriate when counting actual NaN values. A Boolean expression can be tested directly in filter; fill_null(True) changes which unknown rows are retained. The operators & and | combine row-wise Boolean expressions, while Python and/or are not substitutes for column operations.

## Run the lesson

Open `polars-004` in `/classroom`. Its starter `main.py` contains both worked cases, "Two kinds of missing numeric information" and "Unknown predicates and filtering", and prints the dictionary each case returns. The prepared `data-engineering` worker runs it in a fresh temporary directory. An `AssertionError` means that an observation differs from the case's stated contract. The inputs are small literal tables. Cases that demonstrate Parquet scans write their files into a temporary directory that is removed when the case returns. No account, network request or package download is involved. Save source and notes before switching lessons.

## Worked case 1: Two kinds of missing numeric information

The first case separately counts the null and NaN, proves that fill_null leaves NaN untouched, and then applies a declared two-stage conversion. The assertions force the distinction to be visible instead of relying on a printed summary that might obscure it.

**Expected evidence:** One null and one NaN are identified; the chosen final values are [1, 0, 0, 4].

```python
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


if __name__ == "__main__":
    print(example_one())
```

## Worked case 2: Unknown predicates and filtering

The second case contrasts retaining only true rows with retaining true and unknown rows. Its small truth table shows why false AND unknown is false, while true AND unknown remains unknown. These are logical statements about incomplete information.

**Expected evidence:** The default filter retains id 1; an explicit unknown-is-true policy retains ids 1 and 3.

```python
import polars as pl


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


if __name__ == "__main__":
    print(example_two())
```

## Practice

The starter contains both worked cases, so a task can change either one. Make each change in a saved copy, run it, and compare the printed result with the task's check before opening the separate explained answers.

### 1. Count valid finite values

Count observations that are neither null nor NaN.

**Check:** The numeric fixture has 2 such values.

**Hint:** Combine the two validity conditions explicitly.

### 2. Keep a missingness indicator

Add a flag before replacing absent values.

**Check:** The flag identifies the original absent record even after filling.

**Hint:** Transformation order matters.

### 3. Change the denominator

Compute the mean of the two observed finite values and compare with zero filling.

**Check:** Observed mean is 2.5; zero-filled mean is 1.25.

**Hint:** State which records contribute.

### 4. Retain unknown flags

Filter a Boolean field under a keep-unknown policy.

**Check:** Ids 1 and 3 remain.

**Hint:** Use fill_null(True) deliberately.

### 5. Predict logical outcomes

Evaluate false OR unknown and true OR unknown.

**Check:** The answers are unknown and true.

**Hint:** Ask whether the known operand determines the result.

### 6. Detect invalid arithmetic

Generate NaN through an invalid floating operation and keep its cause separate from absent measurement.

**Check:** The diagnostic identifies an arithmetic problem.

**Hint:** Capture validity before replacing values.

## Diagnose errors and misleading results

A surprising row loss may be caused by an unknown predicate, not a filtering bug. Inspect null counts before and after joins and casts. If a mean becomes NaN, count NaNs separately from nulls and trace the operation that introduced them. Do not apply a universal fill-zero policy to counts, measurements, labels and timestamps; they have different semantics.

## Transfer to independent work

Build a table with observed, missing and invalid values, show each inclusion policy, and state which population the resulting statistic describes. Carry that accounting into downstream feature engineering so training and serving apply the same policy.

## Primary references

- [Polars user guide: Missing data](https://docs.pola.rs/user-guide/expressions/missing-data/)
- [Polars Python API reference](https://docs.pola.rs/api/python/stable/reference/index.html)

## Tutor guidance

Use the repository's `$guide-ds60sqlpy-learning` skill (`.agents/skills/guide-ds60sqlpy-learning/SKILL.md`) for `polars-004`. Inspect the learner's own source and printed output first. Ask for an explanation of null, NaN, boolean logic, filter policy and imputation in their own words, then give one focused hint at a time. Keep an assertion on this synthetic fixture separate from a claim about an external dataset or deployed service.
