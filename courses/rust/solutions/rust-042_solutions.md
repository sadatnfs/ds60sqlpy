# rust-042: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-042_solution.rs](rust-042_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Round-trip a complete IPC stream:** Finishing the writer and exhausting the reader establish the bounded stream outcome. The schema and two values round-trip as one complete batch.

**Reject invalid framing:** A binary buffer is not trusted merely because an application labels it Arrow. Arbitrary bytes are rejected as an IPC stream.

## Task answers

### Task 1: Predict and explain

Trace schema, batch and finish operations.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Finishing the writer and exhausting the reader establish the bounded stream outcome. The schema and two values round-trip as one complete batch.

### Task 2: Guided modification

Write two batches with the same schema and count them on readback.

No separate reference answer has been written for this task. Start from Example B: A binary buffer is not trusted merely because an application labels it Arrow. Arbitrary bytes are rejected as an IPC stream.

### Task 3: Independent construction

Build an in-memory IPC round trip preserving a nullable column.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{Array, ArrayRef, Int32Array};
    use arrow::ipc::{reader::StreamReader, writer::StreamWriter};
    use arrow::record_batch::RecordBatch;
    use std::sync::Arc;
    let values: ArrayRef = Arc::new(Int32Array::from(vec![Some(4), None, Some(6)]));
    let batch = RecordBatch::try_from_iter(vec![("qty", values)])?;
    let mut bytes = Vec::new();
    {
        let mut writer = StreamWriter::try_new(&mut bytes, &batch.schema())?;
        writer.write(&batch)?;
        writer.finish()?;
    }
    let mut reader = StreamReader::try_new(std::io::Cursor::new(bytes), None)?;
    let restored = reader.next().unwrap()?;
    assert_eq!(restored.column(0).null_count(), 1);
    assert_eq!(restored, batch);
    Ok(())
}
```

**Observe:** The restored batch equals the original, including its single null.

finish writes the end-of-stream marker, and the reader reproduces the validity buffer, so a null stays a null instead of becoming 0.

### Task 4: Diagnose a defect

Diagnose reading before writer completion or ignoring a reader error.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: IPC is not encryption or authentication. A valid schema can still describe unwanted data. Do not assume a file reader and stream reader accept identical framing.

### Task 5: Boundary evidence

Test malformed bytes and an empty-batch stream with a valid schema.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Round-trip a complete IPC stream) and Example B (Reject invalid framing).

### Task 6: Transfer and justify

Design an IPC transport with size limits, schema checks and explicit ownership of received buffers.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **IPC**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Arrow IPC is a binary interchange format carrying schemas and record batches. It is useful for exchanging Arrow data without converting every value through a text representation. The stream and file formats have different framing and access properties. A stream reader needs a complete schema message before decoding batches, and a writer must be finished to complete its framing.

IPC preserves a representation contract, not an entire application protocol. Bound message sizes, validate schemas and retain ownership of buffers. The classroom writes to an in-memory byte vector and reads it back, so the example remains offline and does not imply an external file-transfer channel exists in the coding pad.

StreamWriter::try_new accepts a writer and schema. write appends a batch; finish closes the stream framing. StreamReader::try_new consumes a reader and optional projection. Each yielded batch is fallible.

IPC is not encryption or authentication. A valid schema can still describe unwanted data. Do not assume a file reader and stream reader accept identical framing.

## Review before continuing

Run the reference and confirm that it prints `rust-042: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
