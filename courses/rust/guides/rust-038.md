# rust-038: Arrow nulls, validity and NaN semantics

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-037`

## Learning objectives

Distinguish null, NaN and valid values in Arrow arrays. The central exercise is task 3: Write a summary returning valid, null and finite counts.

## Purpose and mental model

A null means the logical value is absent under the dataset's policy. The physical value buffer can still contain bytes at that position, but those bytes are not a valid observation. Always consult validity or use an iterator returning Option. Reading value at a null position and treating its physical contents as data can silently corrupt an analysis.

NaN is a floating-point value category, not an Arrow null. It can represent an undefined numerical result while remaining logically present. A pipeline must decide separately how to handle missing and non-finite measurements. Conflating them changes counts, means and validation outcomes.

## Vocabulary and concepts

**Null bitmap:** The validity representation marking absent logical values.

**NaN:** A present floating-point value representing not-a-number.

**Logical value:** The value after applying type and validity semantics.

## How to run this lesson

Beyond the prelude, this lesson's programs use `arrow::array`. A passing run prints `rust-038: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

Array::is_null and is_valid inspect validity. Int32Array::iter yields Option<i32>. Float64Array can contain both Some(NaN) and None. null_count counts absence, not non-finite values.

**Reading Example A (Preserve null versus zero, code below).** `Int32Array::from(vec![Some(0), None, Some(4)])` builds the column from `Option<i32>` values. Arrow stores it as two buffers: a values buffer with one 32-bit slot per row, and a validity bitmap with one bit per row, set for valid and clear for null. The `None` row still occupies a slot in the values buffer; the bitmap is what marks it as missing. `null_count` reports how many bits are clear. `is_valid(0)` and `is_null(1)` read single bits, so a stored zero and a missing value are told apart by the bitmap, not by the number in the slot. `values.iter()` combines both buffers and yields an `Option<i32>` for each row, which is why collecting it reproduces the input exactly. The `&&` in the second assertion requires both checks to hold.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Preserve null versus zero

Optional iteration respects validity rather than exposing meaningless physical contents at null positions.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, Int32Array};
        let values = Int32Array::from(vec![Some(0), None, Some(4)]);
        assert_eq!(values.null_count(), 1);
        assert!(values.is_valid(0) && values.is_null(1));
        assert_eq!(values.iter().collect::<Vec<_>>(), vec![Some(0), None, Some(4)]);
    }
    println!("rust-038: passed");
    Ok(())
}
```

**Observe:** A valid zero and a null remain distinct positions.

### Example B: Keep NaN separate from null

A finite-value policy is an additional analytical rule, not a synonym for Arrow validity.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, Float64Array};
        let values = Float64Array::from(vec![Some(f64::NAN), None, Some(2.0)]);
        assert_eq!(values.null_count(), 1);
        assert!(values.is_valid(0) && values.value(0).is_nan());
        assert_eq!(values.iter().flatten().filter(|value| value.is_finite()).count(), 1);
    }
    println!("rust-038: passed");
    Ok(())
}
```

**Observe:** The column contains one null, one present NaN and one finite value.

## Exercises

1. **Predict and explain.** Classify zero, null and NaN separately.

2. **Guided modification.** Add a present infinity and update finite-value accounting.

3. **Independent construction.** Write a summary returning valid, null and finite counts.

4. **Diagnose a defect.** Diagnose summing physical values without applying validity.

5. **Boundary evidence.** Test all-null, empty and no-null columns.

6. **Transfer and justify.** Define missingness and non-finite policies for a sensor dataset before calculating a mean.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Null positions can contain arbitrary physical values. NaN is not equal to itself under ordinary floating equality. Do not replace every null with zero without a domain justification.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Preserve null versus zero) before changing anything, and confirm its observation: A valid zero and a null remain distinct positions.
2. Compare Example B (Keep NaN separate from null) with Example A and name the first line whose behavior differs. Its observation is: The column contains one null, one present NaN and one finite value.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Null positions can contain arbitrary physical values.

Tempting approaches to rule out before you compare:

- **Task 1.** Treating NaN as missing because both look empty in a report gives `null_count() == 2` in your head while Arrow reports 1, and a mean that drops NaN silently hides a failed calculation.
- **Task 2.** Counting finite values as `len() - null_count()` gives 3 and treats NaN and infinity as usable measurements.
- **Task 5.** Reporting the all-null sum as 0.0 claims a measurement that no row provided.

## Self-check and next step

How does Example A keep the valid zero distinct from the null in the same column? In Example B, why does `null_count()` count the null but not the NaN? What should a sensor mean do with each of them, and why is filling nulls with 0.0 a change of meaning rather than a cleanup?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the Arrow columnar format specification](https://arrow.apache.org/docs/format/Columnar.html) for validity bitmaps and how nulls differ from NaN.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-038: Arrow nulls, validity and NaN semantics.
Read courses/rust/guides/rust-038.md and courses/rust/lessons/rust-038.rs. Prerequisites: rust-037.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-038_solution.rs and
courses/rust/solutions/rust-038_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
