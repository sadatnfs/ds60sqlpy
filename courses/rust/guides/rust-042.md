# rust-042: Arrow IPC and explicit stream completion

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-041`

## Learning objectives

Build an in-memory IPC round trip preserving a nullable column. Then design an IPC transport with size limits, schema checks and explicit ownership of received buffers.

## Purpose and mental model

Arrow IPC is a binary interchange format carrying schemas and record batches. It is useful for exchanging Arrow data without converting every value through a text representation. The stream and file formats have different framing and access properties. A stream reader needs a complete schema message before decoding batches, and a writer must be finished to complete its framing.

IPC preserves a representation contract, not an entire application protocol. Bound message sizes, validate schemas and retain ownership of buffers. The classroom writes to an in-memory byte vector and reads it back, so the example remains offline and does not imply an external file-transfer channel exists in the coding pad.

## Vocabulary and concepts

**IPC:** Inter-process communication format for Arrow schemas and batches.

**Framing:** The structure separating messages in a byte stream.

**Round trip:** Encoding and decoding while checking retained logical meaning.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

StreamWriter::try_new accepts a writer and schema. write appends a batch; finish closes the stream framing. StreamReader::try_new consumes a reader and optional projection. Each yielded batch is fallible.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Round-trip a complete IPC stream

Finishing the writer and exhausting the reader establish the bounded stream outcome.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::sync::Arc;
        use std::io::Cursor;
        use arrow::array::{ArrayRef, Int32Array};
        use arrow::record_batch::RecordBatch;
        use arrow::ipc::{reader::StreamReader, writer::StreamWriter};
        let batch = RecordBatch::try_from_iter(vec![("quantity", Arc::new(Int32Array::from(vec![2, 3])) as ArrayRef)])?;
        let mut bytes = Vec::new();
        { let mut writer = StreamWriter::try_new(&mut bytes, &batch.schema())?; writer.write(&batch)?; writer.finish()?; }
        let mut reader = StreamReader::try_new(Cursor::new(bytes), None)?;
        let restored = reader.next().unwrap()?;
        assert_eq!(restored, batch);
        assert!(reader.next().is_none());
    }
    println!("rust-042: passed");
    Ok(())
}
```

**Observe:** The schema and two values round-trip as one complete batch.

### Example B: Reject invalid framing

A binary buffer is not trusted merely because an application labels it Arrow.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::io::Cursor;
        use arrow::ipc::reader::StreamReader;
        assert!(StreamReader::try_new(Cursor::new(vec![1_u8, 2, 3]), None).is_err());
    }
    println!("rust-042: passed");
    Ok(())
}
```

**Observe:** Arbitrary bytes are rejected as an IPC stream.

## Exercises

1. **Predict and explain.** Trace schema, batch and finish operations.

2. **Guided modification.** Write two batches with the same schema and count them on readback.

3. **Independent construction.** Build an in-memory IPC round trip preserving a nullable column.

4. **Diagnose a defect.** Diagnose reading before writer completion or ignoring a reader error.

5. **Boundary evidence.** Test malformed bytes and an empty-batch stream with a valid schema.

6. **Transfer and justify.** Design an IPC transport with size limits, schema checks and explicit ownership of received buffers.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

IPC is not encryption or authentication. A valid schema can still describe unwanted data. Do not assume a file reader and stream reader accept identical framing.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain IPC, Framing, Round trip without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://arrow.apache.org/docs/format/Columnar.html#serialization-and-interprocess-communication-ipc). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-042: Arrow IPC and explicit stream completion.
Read courses/rust/guides/rust-042.md and courses/rust/lessons/rust-042.rs. Prerequisites: rust-041.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-042_solution.rs and
courses/rust/solutions/rust-042_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
