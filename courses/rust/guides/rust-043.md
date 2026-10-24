# rust-043: CSV and JSON readers with explicit schemas

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-042`

## Learning objectives

Read a small nullable dataset and validate its domain ranges afterward. Then design an inference-to-reviewed-schema workflow with checks for later type and nullability drift.

## Purpose and mental model

CSV and JSON are external representations with their own syntax and ambiguity. CSV supports quoted delimiters and escaped quotes, so a naive split is not a general parser. JSON can contain fields with inconsistent types across records. An explicit Arrow schema gives the reader a target contract and makes incompatible values visible.

Automatic inference is useful exploration but should not silently become a production schema policy. A sample may miss later nulls or wider numeric ranges. Bound input size and batch size, inspect errors and validate domain constraints after decoding. The prepared crate includes actual CSV and newline-delimited JSON reader features; no separate package is fetched during a run.

## Vocabulary and concepts

**Schema inference:** Estimating a schema from observed data.

**NDJSON:** JSON objects separated by newlines for record-oriented streaming.

**Batch size:** The maximum records targeted in one reader output batch.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

CSV ReaderBuilder takes a schema and with_header policy. JSON ReaderBuilder consumes newline-delimited object records. Both readers yield fallible RecordBatch values, and batch size bounds one produced chunk.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Read CSV through its real parser

Header handling and column types are deliberate rather than guessed from a hand-written split.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::sync::Arc;
        use std::io::Cursor;
        use arrow::datatypes::{DataType, Field, Schema};
        let schema = Arc::new(Schema::new(vec![Field::new("name", DataType::Utf8, false), Field::new("quantity", DataType::Int32, false)]));
        let input = b"name,quantity\npear,2\napple,3\n";
        let mut reader = arrow::csv::ReaderBuilder::new(schema).with_header(true).with_batch_size(8).build(Cursor::new(input))?;
        let batch = reader.next().unwrap()?;
        assert_eq!((batch.num_rows(), batch.num_columns()), (2, 2));
        assert_eq!(batch.column(0).as_any().downcast_ref::<arrow::array::StringArray>().unwrap().value(0), "pear");
    }
    println!("rust-043: passed");
    Ok(())
}
```

**Observe:** The parser produces two rows under the explicit schema.

### Example B: Read newline-delimited JSON

Structural decoding retains missingness rather than converting it to zero.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::sync::Arc;
        use std::io::Cursor;
        use arrow::array::Int32Array;
        use arrow::datatypes::{DataType, Field, Schema};
        let schema = Arc::new(Schema::new(vec![Field::new("quantity", DataType::Int32, true)]));
        let input = b"{\"quantity\":2}\n{\"quantity\":null}\n";
        let mut reader = arrow::json::ReaderBuilder::new(schema).with_batch_size(8).build(Cursor::new(input))?;
        let batch = reader.next().unwrap()?;
        let values = batch.column(0).as_any().downcast_ref::<Int32Array>().unwrap();
        assert_eq!(values.iter().collect::<Vec<_>>(), vec![Some(2), None]);
    }
    println!("rust-043: passed");
    Ok(())
}
```

**Observe:** JSON null becomes Arrow null under the declared nullable field.

## Exercises

1. **Predict and explain.** State the schema and framing expected by each reader.

2. **Guided modification.** Add a CSV quoted field containing a comma and inspect its single parsed value.

3. **Independent construction.** Read a small nullable dataset and validate its domain ranges afterward.

4. **Diagnose a defect.** Diagnose using the foundation split_once parser for general quoted CSV.

5. **Boundary evidence.** Test malformed numeric text, explicit null and records spanning more than one batch.

6. **Transfer and justify.** Design an inference-to-reviewed-schema workflow with checks for later type and nullability drift.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

NDJSON is not a single enclosing JSON array. Reader success does not establish domain validity. Always handle each yielded batch error rather than counting only successful batches.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Schema inference, NDJSON, Batch size without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.rs/arrow/60.0.0/arrow/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-043: CSV and JSON readers with explicit schemas.
Read courses/rust/guides/rust-043.md and courses/rust/lessons/rust-043.rs. Prerequisites: rust-042.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-043_solution.rs and
courses/rust/solutions/rust-043_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
