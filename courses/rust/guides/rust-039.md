# rust-039: Schemas, fields and RecordBatch invariants

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-038`

## Learning objectives

Construct a batch for a small validated inventory dataset. Then design a schema evolution policy that preserves names, units and saved data meaning.

## Purpose and mental model

A Schema gives columns names, logical types, nullability and optional metadata. A RecordBatch pairs that schema with arrays representing one batch of rows. The arrays must match the schema types and have compatible lengths. This is a useful executable contract at a data boundary.

A batch is not the entire dataset and does not imply a global uniqueness or ordering guarantee. Several batches can share a schema while representing different chunks. Validate domain rules such as unique IDs separately. A schema mismatch should remain an error rather than being repaired by silently dropping or reordering columns.

## Vocabulary and concepts

**Schema:** A contract for column names, types and nullability.

**RecordBatch:** Equal-length columns representing one batch of rows.

**ArrayRef:** Shared ownership of a type-erased Arrow array.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

Field::new records name, DataType and nullable policy. Schema::new groups fields. RecordBatch::try_new validates arrays against an Arc<Schema>. ArrayRef stores different concrete arrays behind one shared interface.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Build an aligned batch

Names and types are explicit rather than inferred from arbitrary array positions.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::sync::Arc;
        use arrow::array::{ArrayRef, Int32Array, StringArray};
        use arrow::datatypes::{DataType, Field, Schema};
        use arrow::record_batch::RecordBatch;
        let schema = Arc::new(Schema::new(vec![Field::new("name", DataType::Utf8, false), Field::new("quantity", DataType::Int32, false)]));
        let columns: Vec<ArrayRef> = vec![Arc::new(StringArray::from(vec!["pear", "apple"])), Arc::new(Int32Array::from(vec![2, 3]))];
        let batch = RecordBatch::try_new(schema, columns)?;
        assert_eq!((batch.num_rows(), batch.num_columns()), (2, 2));
        assert_eq!(batch.column(0).as_any().downcast_ref::<arrow::array::StringArray>().unwrap().value(0), "pear");
    }
    println!("rust-039: passed");
    Ok(())
}
```

**Observe:** Two aligned columns form a two-row, two-column batch.

### Example B: Reject incompatible lengths

A batch cannot invent which row a shorter column should align with.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::sync::Arc;
        use arrow::array::{ArrayRef, Int32Array};
        use arrow::datatypes::{DataType, Field, Schema};
        use arrow::record_batch::RecordBatch;
        let schema = Arc::new(Schema::new(vec![Field::new("a", DataType::Int32, false), Field::new("b", DataType::Int32, false)]));
        let columns: Vec<ArrayRef> = vec![Arc::new(Int32Array::from(vec![1, 2])), Arc::new(Int32Array::from(vec![3]))];
        assert!(RecordBatch::try_new(schema, columns).is_err());
    }
    println!("rust-039: passed");
    Ok(())
}
```

**Observe:** Unequal column lengths are rejected.

## Exercises

1. **Predict and explain.** State the row grain and schema of the valid batch.

2. **Guided modification.** Add a nullable numeric field with matching length.

3. **Independent construction.** Construct a batch for a small validated inventory dataset.

4. **Diagnose a defect.** Diagnose swapping arrays while retaining the old field order.

5. **Boundary evidence.** Test type mismatch, length mismatch and a zero-row batch.

6. **Transfer and justify.** Design a schema evolution policy that preserves names, units and saved data meaning.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A nullable field permits nulls; it does not require them. Schema validation does not establish unique keys or domain ranges. Do not infer whole-dataset row count from one batch.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Schema, RecordBatch, ArrayRef without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.rs/arrow/60.0.0/arrow/record_batch/struct.RecordBatch.html). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-039: Schemas, fields and RecordBatch invariants.
Read courses/rust/guides/rust-039.md and courses/rust/lessons/rust-039.rs. Prerequisites: rust-038.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-039_solution.rs and
courses/rust/solutions/rust-039_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
