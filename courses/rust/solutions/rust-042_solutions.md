# rust-042: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-042_solution.rs](rust-042_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Round-trip a complete IPC stream:** Finishing the writer and exhausting the reader establish the bounded stream outcome. The schema and two values round-trip as one complete batch.

**Reject invalid framing:** A binary buffer is not trusted merely because an application labels it Arrow. Arbitrary bytes are rejected as an IPC stream.

## Task answers

### Task 1: Predict and explain

Trace schema, batch and finish operations.

**Written answer.** `StreamWriter::try_new` writes the schema message first, which tells a reader the field `quantity` and its `Int32` type. `writer.write(&batch)` appends one record batch message holding the two values. `writer.finish()` appends the end-of-stream marker. On the reading side, `StreamReader::try_new` reads and checks the schema, the first `next()` returns the batch, and the second `next()` returns `None` because the stream ended.

**Why it is correct.** The stream is framed as one schema, then zero or more batches, then an end marker. Every operation in Example A corresponds to exactly one of those parts.

**Plausible wrong approach.** Thinking `try_new` on the writer writes nothing until the first batch predicts that a stream with no batches is empty bytes. Task 5 shows the schema is still there.

**How to verify.** Print `bytes.len()` after `try_new`, after `write` and after `finish`: the buffer grows at each step.

### Task 2: Guided modification

Write two batches with the same schema and count them on readback.

**Reference answer.** The same statements run as the `Task 2` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{ArrayRef, Int32Array};
    use arrow::ipc::{reader::StreamReader, writer::StreamWriter};
    use arrow::record_batch::RecordBatch;
    use std::sync::Arc;
    let first = RecordBatch::try_from_iter(vec![(
        "quantity",
        Arc::new(Int32Array::from(vec![2, 3])) as ArrayRef,
    )])?;
    let second = RecordBatch::try_from_iter(vec![(
        "quantity",
        Arc::new(Int32Array::from(vec![5])) as ArrayRef,
    )])?;
    assert_eq!(first.schema(), second.schema());
    let mut bytes = Vec::new();
    {
        let mut writer = StreamWriter::try_new(&mut bytes, &first.schema())?;
        writer.write(&first)?;
        writer.write(&second)?;
        writer.finish()?;
    }
    let reader = StreamReader::try_new(std::io::Cursor::new(bytes), None)?;
    let mut batches = 0;
    let mut rows = 0;
    for batch in reader {
        let batch = batch?;
        batches += 1;
        rows += batch.num_rows();
    }
    assert_eq!((batches, rows), (2, 3));
    Ok(())
}
```

**Observe:** The reader yields two batches holding three rows in total.

One schema message is followed by two batch messages, so the reader reports each batch separately and does not merge them. The `?` on every yielded item means a damaged message stops the count instead of being skipped.

**Plausible wrong approach.** Counting rows from only the first `next()` reports 2 and treats one batch as the whole stream.

**How to verify.** Run the block. Remove `writer.write(&second)?;` and the result becomes (1, 2).

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

**Written answer.** Two related defects. First, using `bytes` while the writer still borrows it, for example passing `bytes.clone()` to a reader before the writer's block ends, is rejected with E0502, because the writer holds a mutable borrow. Second, dropping the writer without `finish()`: in the reference run the reader then returned the one batch and `None`, exactly like a complete stream, so the missing end marker went unnoticed. Cutting 10 bytes off the stream instead made the reader return an error, failed to fill whole buffer, and code that iterates with `.flatten()` or `filter_map(Result::ok)` silently drops that error and reports a short result.

**Why it is correct.** The reader can only judge the bytes it receives. Calling `finish()` is the writer's statement that the stream is complete, and handling every `Result` from the reader is the only way a truncated message becomes visible.

**Plausible wrong approach.** Assuming that a successful readback proves the writer called `finish()` is wrong here: the unfinished stream read back the same batch.

**How to verify.** Write one batch without `finish()`, truncate the last 10 bytes, and iterate with `?`: the reader returns the I/O error instead of a silent short count.

### Task 5: Boundary evidence

Test malformed bytes and an empty-batch stream with a valid schema.

**Reference answer.** The same statements run as the `Task 5` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{ArrayRef, Int32Array};
    use arrow::ipc::{reader::StreamReader, writer::StreamWriter};
    use arrow::record_batch::RecordBatch;
    use std::io::Cursor;
    use std::sync::Arc;
    assert!(StreamReader::try_new(Cursor::new(Vec::<u8>::new()), None).is_err());
    assert!(StreamReader::try_new(Cursor::new(vec![0xFF_u8; 8]), None).is_err());
    let template = RecordBatch::try_from_iter(vec![(
        "quantity",
        Arc::new(Int32Array::from(vec![1])) as ArrayRef,
    )])?;
    let schema = template.schema();
    let mut bytes = Vec::new();
    {
        let mut writer = StreamWriter::try_new(&mut bytes, &schema)?;
        writer.write(&template.slice(0, 0))?;
        writer.finish()?;
    }
    let mut reader = StreamReader::try_new(Cursor::new(bytes), None)?;
    assert_eq!(reader.schema(), schema);
    let empty = reader.next().unwrap()?;
    assert_eq!(empty.num_rows(), 0);
    assert!(reader.next().is_none());
    Ok(())
}
```

**Observe:** Empty bytes and eight bytes of 0xFF are both rejected, while a stream with a valid schema and one zero-row batch reads back that schema, one empty batch and then the end.

Malformed framing fails at `try_new`, before any batch is produced. A zero-row batch is valid data: the stream still carries the schema, so a consumer can tell "no rows" from "no stream".

**Plausible wrong approach.** Treating the empty-batch stream as an error, or treating the malformed bytes as zero rows, erases the difference between a valid empty result and a broken input.

**How to verify.** Run the block. Remove the `writer.write` line and the reader yields no batch at all, with the schema still intact.

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
