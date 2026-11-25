# rust-038: explanation and comparison

Executable reference: [rust-038_solution.rs](rust-038_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Preserve null versus zero:** Optional iteration respects validity rather than exposing meaningless physical contents at null positions. A valid zero and a null remain distinct positions.

**Keep NaN separate from null:** A finite-value policy is an additional analytical rule, not a synonym for Arrow validity. The column contains one null, one present NaN and one finite value.

## Task answers

### Task 1: Predict and explain

Classify zero, null and NaN separately.

**Written answer.** In Example A, position 0 is a valid zero: present, known and equal to 0. Position 1 is null, so its validity bit is unset and no value is known. In Example B, position 0 is NaN: valid and present, but its value is the floating-point result "not a number". Position 1 is null again, and position 2 is the only finite value. So zero is data, null is missing data, and NaN is present data outside the finite numbers.

**Why it is correct.** Validity and floating-point classification are separate layers: the null bitmap says whether a slot holds data, and `is_nan` and `is_finite` describe the value in a valid slot. Each needs its own policy.

**Plausible wrong approach.** Treating NaN as missing because both look empty in a report gives `null_count() == 2` in your head while Arrow reports 1, and a mean that drops NaN silently hides a failed calculation.

**How to verify.** Assert `values.is_valid(0) && values.value(0).is_nan()` and `values.is_null(1)` on Example B: one present NaN, one null.

### Task 2: Guided modification

Add a present infinity and update finite-value accounting.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 2` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{Array, Float64Array};
    let values = Float64Array::from(vec![Some(f64::NAN), None, Some(2.0), Some(f64::INFINITY)]);
    let present: Vec<f64> = values.iter().flatten().collect();
    assert_eq!(values.null_count(), 1);
    assert_eq!(present.len(), 3);
    assert_eq!(present.iter().filter(|value| value.is_finite()).count(), 1);
    assert_eq!(
        present.iter().filter(|value| value.is_infinite()).count(),
        1
    );
    assert_eq!(present.iter().filter(|value| value.is_nan()).count(), 1);
    Ok(())
}
```

**Observe:** The column now holds one null and three present values: one finite, one infinite and one NaN.

Infinity is a present, non-null value, so validity is unchanged and only the finite-value count needs a new category. `is_finite` excludes both NaN and the infinities, which is why the finite count stays at 1 when a valid value is added.

**Plausible wrong approach.** Counting finite values as `len() - null_count()` gives 3 and treats NaN and infinity as usable measurements.

**How to verify.** Run the block. Replace infinity with `Some(5.0)` and the finite count becomes 2 while the null count stays 1.

### Task 3: Independent construction

Write a summary returning valid, null and finite counts.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{Array, Float64Array};
    fn summary(values: &Float64Array) -> (usize, usize, usize) {
        let valid = values.len() - values.null_count();
        let finite = values.iter().flatten().filter(|v| v.is_finite()).count();
        (valid, values.null_count(), finite)
    }
    let values = Float64Array::from(vec![Some(1.5), None, Some(f64::NAN), Some(2.0)]);
    assert_eq!(summary(&values), (3, 1, 2));
    Ok(())
}
```

**Observe:** Four slots give 3 valid values, 1 null and 2 finite values.

Validity and finiteness are different questions: NaN is a valid, non-null value that is not finite, while the null slot has no value at all.

### Task 4: Diagnose a defect

Diagnose summing physical values without applying validity.

**Written answer.** The defect is summing the physical buffer, `values.values().iter().sum::<i32>()`, which also adds whatever is stored in null slots. With `Int32Array::new(vec![5, 99, 4].into(), Some(NullBuffer::from(vec![true, false, true])))` that sum is 108, while the valid values sum to 9. Apply validity first: `values.iter().flatten().sum::<i32>()` or `arrow::compute::sum(&values)`, which returns `Some(9)`.

**Why it is correct.** Arrow promises nothing about the physical contents of a null slot; only the validity bitmap says which slots hold data. Any aggregate that reads `values()` directly must apply that bitmap itself.

**Plausible wrong approach.** Testing with `Int32Array::from(vec![Some(5), None, Some(4)])` happens to store 0 in the null slot, so the buggy sum looks correct and the defect survives.

**How to verify.** Build the array with the explicit 99 under the null and compare the two sums: 108 against 9.

### Task 5: Boundary evidence

Test all-null, empty and no-null columns.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 5` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{Array, Float64Array};
    fn counts(values: &Float64Array) -> (usize, usize, usize) {
        let finite = values
            .iter()
            .flatten()
            .filter(|value| value.is_finite())
            .count();
        (
            values.len() - values.null_count(),
            values.null_count(),
            finite,
        )
    }
    let all_null = Float64Array::from(vec![None, None, None]);
    let empty = Float64Array::from(Vec::<f64>::new());
    let no_null = Float64Array::from(vec![1.0, f64::NAN, -3.5]);
    assert_eq!(counts(&all_null), (0, 3, 0));
    assert_eq!(counts(&empty), (0, 0, 0));
    assert_eq!(counts(&no_null), (3, 0, 2));
    assert!(no_null.nulls().is_none());
    assert_eq!(arrow::compute::sum(&all_null), None);
    Ok(())
}
```

**Observe:** All-null gives (0, 3, 0), empty gives (0, 0, 0) and the no-null column gives (3, 0, 2); it carries no null buffer at all, and the sum of an all-null column is None.

All-null and empty both have zero valid values, but only the null count tells them apart: three missing rows are not zero rows. A column without nulls may omit the validity buffer entirely, so code must not assume one exists. `sum` returns `None` when there are no valid values, rather than an invented 0.

**Plausible wrong approach.** Reporting the all-null sum as 0.0 claims a measurement that no row provided.

**How to verify.** Run the block. Replace one `None` with `Some(0.0)` and the all-null case becomes (1, 2, 1) with a sum of Some(0.0).

### Task 6: Transfer and justify

Define missingness and non-finite policies for a sensor dataset before calculating a mean.

**Judging criteria.** A strong policy defines both cases before computing. A null means no reading: exclude it from the mean and report how many there were, or reject the batch above a stated threshold. NaN and infinity mean a reading arrived but is not a usable number: reject them explicitly, count them separately, and never let one silently turn the whole mean into NaN. The report gives the mean with its valid, null and non-finite counts. State one limitation: excluding values biases the mean when readings go missing for reasons related to their value.

## Mechanism and diagnostic reasoning

A null means the logical value is absent under the dataset's policy. The physical value buffer can still contain bytes at that position, but those bytes are not a valid observation. Always consult validity or use an iterator returning Option. Reading value at a null position and treating its physical contents as data can silently corrupt an analysis.

NaN is a floating-point value category, not an Arrow null. It can represent an undefined numerical result while remaining logically present. A pipeline must decide separately how to handle missing and non-finite measurements. Conflating them changes counts, means and validation outcomes.

Array::is_null and is_valid inspect validity. Int32Array::iter yields Option<i32>. Float64Array can contain both Some(NaN) and None. null_count counts absence, not non-finite values.

Null positions can contain arbitrary physical values. NaN is not equal to itself under ordinary floating equality. Do not replace every null with zero without a domain justification.

## Review before continuing

Rebuild Example B (Keep NaN separate from null) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
