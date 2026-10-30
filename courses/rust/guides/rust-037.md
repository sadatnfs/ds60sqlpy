# rust-037: Arrow columnar memory and typed arrays

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-036`

## Learning objectives

Construct paired integer and text columns with equal row counts. Then compare row-object and columnar representations for a repeated analytical scan.

## Purpose and mental model

Apache Arrow defines a columnar in-memory representation for analytical data. A typed array stores values of one logical type along with validity information and, for variable-width types, offsets and data buffers. This differs from a collection of row objects with independent allocations for every field.

Columnar layout can make scans and vectorized operations efficient, but Arrow is not a database, query optimizer or automatic distributed engine. Its arrays provide a representation and compute building blocks. The prepared Arrow 60 crate is real library code linked into the worker. Begin with typed arrays and the Array trait before using type-erased columns in a RecordBatch.

## Vocabulary and concepts

**Columnar layout:** Grouping values by column rather than storing independent row objects.

**Typed array:** An Arrow array with a known concrete element representation.

**Validity:** Information identifying which logical positions are null.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

Int32Array stores signed 32-bit integer values. Importing the Array trait exposes common methods such as len and null_count. StringArray stores variable-width UTF-8 values. ArrayRef later erases concrete type behind Arc<dyn Array>.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Create a concrete integer column

The trait supplies common array behavior while the concrete type supplies typed value access.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, Int32Array};
        let values = Int32Array::from(vec![2, 4, 6]);
        assert_eq!(values.len(), 3);
        assert_eq!(values.value(1), 4);
        assert_eq!(values.null_count(), 0);
    }
    println!("rust-037: passed");
    Ok(())
}
```

**Observe:** The concrete column contains three non-null integers.

### Example B: Use a variable-width text column

Offsets and UTF-8 data support variable-width values without pretending every row has a fixed-size string slot.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use arrow::array::{Array, StringArray};
        let labels = StringArray::from(vec!["a", "longer", "é"]);
        assert_eq!(labels.len(), 3);
        assert_eq!(labels.value(1), "longer");
        assert_eq!(labels.value(2), "é");
    }
    println!("rust-037: passed");
    Ok(())
}
```

**Observe:** Different text lengths share one logical column.

## Exercises

1. **Predict and explain.** Identify logical length, type and null count.

2. **Guided modification.** Add a fourth value and inspect its typed access.

3. **Independent construction.** Construct paired integer and text columns with equal row counts.

4. **Diagnose a defect.** Diagnose treating Arrow as an automatically installed SQL engine.

5. **Boundary evidence.** Test an empty typed array and a non-ASCII string.

6. **Transfer and justify.** Compare row-object and columnar representations for a repeated analytical scan.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Value access at an invalid index still violates bounds. A library being linked does not mean every optional Arrow feature is enabled. Parquet and DataFusion are separate crates and workflows.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Columnar layout, Typed array, Validity without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.rs/arrow/60.0.0/arrow/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-037: Arrow columnar memory and typed arrays.
Read courses/rust/guides/rust-037.md and courses/rust/lessons/rust-037.rs. Prerequisites: rust-036.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-037_solution.rs and
courses/rust/solutions/rust-037_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
