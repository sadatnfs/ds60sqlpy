# rust-038: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-038_solution.rs](rust-038_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Preserve null versus zero:** Optional iteration respects validity rather than exposing meaningless physical contents at null positions. A valid zero and a null remain distinct positions.

**Keep NaN separate from null:** A finite-value policy is an additional analytical rule, not a synonym for Arrow validity. The column contains one null, one present NaN and one finite value.

## Task answers

### Task 1: Predict and explain

Classify zero, null and NaN separately.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Optional iteration respects validity rather than exposing meaningless physical contents at null positions. A valid zero and a null remain distinct positions.

### Task 2: Guided modification

Add a present infinity and update finite-value accounting.

No separate reference answer has been written for this task. Start from Example B: A finite-value policy is an additional analytical rule, not a synonym for Arrow validity. The column contains one null, one present NaN and one finite value.

### Task 3: Independent construction

Write a summary returning valid, null and finite counts.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

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

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Null positions can contain arbitrary physical values. NaN is not equal to itself under ordinary floating equality. Do not replace every null with zero without a domain justification.

### Task 5: Boundary evidence

Test all-null, empty and no-null columns.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Preserve null versus zero) and Example B (Keep NaN separate from null).

### Task 6: Transfer and justify

Define missingness and non-finite policies for a sensor dataset before calculating a mean.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Null bitmap**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A null means the logical value is absent under the dataset's policy. The physical value buffer can still contain bytes at that position, but those bytes are not a valid observation. Always consult validity or use an iterator returning Option. Reading value at a null position and treating its physical contents as data can silently corrupt an analysis.

NaN is a floating-point value category, not an Arrow null. It can represent an undefined numerical result while remaining logically present. A pipeline must decide separately how to handle missing and non-finite measurements. Conflating them changes counts, means and validation outcomes.

Array::is_null and is_valid inspect validity. Int32Array::iter yields Option<i32>. Float64Array can contain both Some(NaN) and None. null_count counts absence, not non-finite values.

Null positions can contain arbitrary physical values. NaN is not equal to itself under ordinary floating equality. Do not replace every null with zero without a domain justification.

## Review before continuing

Run the reference and confirm that it prints `rust-038: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
