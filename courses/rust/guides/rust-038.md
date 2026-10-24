# rust-038: Arrow nulls, validity and NaN semantics

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-037`

## Learning objectives

Write a summary returning valid, null and finite counts. Then define missingness and non-finite policies for a sensor dataset before calculating a mean.

## Purpose and mental model

A null means the logical value is absent under the dataset's policy. The physical value buffer can still contain bytes at that position, but those bytes are not a valid observation. Always consult validity or use an iterator returning Option. Reading value at a null position and treating its physical contents as data can silently corrupt an analysis.

NaN is a floating-point value category, not an Arrow null. It can represent an undefined numerical result while remaining logically present. A pipeline must decide separately how to handle missing and non-finite measurements. Conflating them changes counts, means and validation outcomes.

## Vocabulary and concepts

**Null bitmap:** The validity representation marking absent logical values.

**NaN:** A present floating-point value representing not-a-number.

**Logical value:** The value after applying type and validity semantics.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

Array::is_null and is_valid inspect validity. Int32Array::iter yields Option<i32>. Float64Array can contain both Some(NaN) and None. null_count counts absence, not non-finite values.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Null positions can contain arbitrary physical values. NaN is not equal to itself under ordinary floating equality. Do not replace every null with zero without a domain justification.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Null bitmap, NaN, Logical value without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://arrow.apache.org/docs/format/Columnar.html). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
