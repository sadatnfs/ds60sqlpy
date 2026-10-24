# rust-048: Capstone: a validated Arrow analytical report

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-047`

## Learning objectives

Build a multi-column RecordBatch report and round-trip it through IPC. Then deliver a project README with schema, ownership, bounds, failure policies, actual runtime evidence and one independent Arrow extension.

## Purpose and mental model

The final project combines a schema, nullable columns, domain admission and a deterministic report. Arrow provides the representation and kernels; the application owns what counts as a valid measurement and how rejection is reported. A correct total must state its population and handling of missing values.

Build the portable kernel first, then extend the external InventoryLab or a separately prepared Arrow Cargo project. Keep package resolution, source compilation, runtime assertions, browser delivery and cross-language interchange evidence separate. Expert practice includes explaining limits and diagnosing unfamiliar failures, not assuming a finite tutorial covers every library or production architecture.

## Vocabulary and concepts

**Analytical contract:** The population, units and missingness rules defining a calculation.

**Acceptance evidence:** Observed results establishing a declared requirement.

**Extension boundary:** A deliberate interface for adding a new capability.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.

Use [InventoryLab](../fixtures/InventoryLab/README.md) for the real library/project structure. The Arrow classroom dependency is already prepared; any independent Cargo project must deliberately prepare and lock Arrow60 before claiming offline builds.

## Syntax anatomy and execution trace

A typed nullable array exposes valid values through Option iteration. The application can count nulls, reject negative present values and sum the admitted population. A stable report record makes those decisions inspectable.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Summarize a nullable measurement column

The calculation preserves a complete accounting of its five input positions.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, Int32Array};
        let values = Int32Array::from(vec![Some(2), None, Some(3), Some(-1), Some(0)]);
        let accepted: Vec<_> = values.iter().flatten().filter(|value| *value >= 0).collect();
        assert_eq!(accepted.iter().sum::<i32>(), 5);
        assert_eq!(accepted.len(), 3);
        assert_eq!(values.null_count(), 1);
        assert_eq!(values.len() - values.null_count() - accepted.len(), 1);
    }
    println!("rust-048: passed");
    Ok(())
}
```

**Observe:** Three valid nonnegative values total five, alongside one null and one rejected negative.

### Example B: Keep empty and all-null data distinct

A total of zero alone cannot express this distinction.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, Int32Array};
        let empty = Int32Array::from(Vec::<Option<i32>>::new());
        let missing = Int32Array::from(vec![None::<i32>, None]);
        assert_eq!((empty.len(), empty.null_count()), (0, 0));
        assert_eq!((missing.len(), missing.null_count()), (2, 2));
    }
    println!("rust-048: passed");
    Ok(())
}
```

**Observe:** No submitted rows and two missing observations remain different reports.

## Exercises

1. **Predict and explain.** Trace each value to accepted, null or rejected accounting.

2. **Guided modification.** Add another valid value and independently derive the new report.

3. **Independent construction.** Build a multi-column RecordBatch report and round-trip it through IPC.

4. **Diagnose a defect.** Introduce and diagnose a null-as-zero, schema-order or duplicate-row defect.

5. **Boundary evidence.** Test empty, all-null, all-rejected, overflow and malformed-input boundaries.

6. **Transfer and justify.** Deliver a project README with schema, ownership, bounds, failure policies, actual runtime evidence and one independent Arrow extension.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A passing kernel does not prove external storage, authentication or every architecture. Do not label Parquet, DataFusion or a distributed service supported without explicit dependency and runtime qualification. Retain source-bound evidence for the program actually executed.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Analytical contract, Acceptance evidence, Extension boundary without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.rs/arrow/60.0.0/arrow/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-048: Capstone: a validated Arrow analytical report.
Read courses/rust/guides/rust-048.md and courses/rust/lessons/rust-048.rs. Prerequisites: rust-047.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-048_solution.rs and
courses/rust/solutions/rust-048_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
