# rust-042: Arrow IPC and explicit stream completion

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-041`

## Learning objectives

Round-trip RecordBatches through Arrow IPC streams with explicit completion. The central exercise is task 3: Build an in-memory IPC round trip preserving a nullable column.

## Purpose and mental model

Arrow IPC is a binary interchange format carrying schemas and record batches. It is useful for exchanging Arrow data without converting every value through a text representation. The stream and file formats have different framing and access properties. A stream reader needs a complete schema message before decoding batches, and a writer must be finished to complete its framing.

IPC preserves a representation contract, not an entire application protocol. Bound message sizes, validate schemas and retain ownership of buffers. The classroom writes to an in-memory byte vector and reads it back, so the example remains offline and does not imply an external file-transfer channel exists in the coding pad.

## Vocabulary and concepts

**IPC:** Inter-process communication format for Arrow schemas and batches.

**Framing:** The structure separating messages in a byte stream.

**Round trip:** Encoding and decoding while checking retained logical meaning.

## How to run this lesson

Beyond the prelude, this lesson's programs use `arrow::array`, `arrow::ipc`, `arrow::record_batch`, `std::io` and `std::sync`. A passing run prints `rust-042: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

StreamWriter::try_new accepts a writer and schema. write appends a batch; finish closes the stream framing. StreamReader::try_new consumes a reader and optional projection. Each yielded batch is fallible.

**Reading Example A (Round-trip a complete IPC stream, code below).** `RecordBatch::try_from_iter` builds a batch from `(name, ArrayRef)` pairs and infers its schema from the column names and array types; the `as ArrayRef` cast erases the concrete array type. `StreamWriter::try_new(&mut bytes, &batch.schema())` holds a mutable borrow of the byte vector for as long as the writer exists. The inner `{ }` block bounds that borrow, so after it closes, `bytes` can be moved into a `Cursor`, which gives an in-memory `Vec<u8>` the `Read` trait. In `StreamReader::try_new(..., None)`, the second argument is an optional column projection. The reader is an iterator of `Result<RecordBatch, ArrowError>`, so `reader.next()` yields an `Option` of a `Result`, which is why the code writes `unwrap()?`.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

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
        {
            let mut writer = StreamWriter::try_new(&mut bytes, &batch.schema())?;
            writer.write(&batch)?;
            writer.finish()?;
        }
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

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

IPC is not encryption or authentication. A valid schema can still describe unwanted data. Do not assume a file reader and stream reader accept identical framing.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Round-trip a complete IPC stream) before changing anything, and confirm its observation: The schema and two values round-trip as one complete batch.
2. Compare Example B (Reject invalid framing) with Example A and name the first line whose behavior differs. Its observation is: Arbitrary bytes are rejected as an IPC stream.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: IPC is not encryption or authentication.

Tempting approaches to rule out before you compare:

- **Task 1.** Thinking `try_new` on the writer writes nothing until the first batch predicts that a stream with no batches is empty bytes. Task 5 shows the schema is still there.
- **Task 2.** Counting rows from only the first `next()` reports 2 and treats one batch as the whole stream.
- **Task 5.** Treating the empty-batch stream as an error, or treating the malformed bytes as zero rows, erases the difference between a valid empty result and a broken input.

## Self-check and next step

What does Example A's stream carry before its first batch, and what does `reader.next()` return after the last one? Why does Example B reject three arbitrary bytes when the reader is created, instead of yielding an empty stream? Which properties must the round trip preserve beyond the two values themselves?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the Arrow IPC specification](https://arrow.apache.org/docs/format/Columnar.html#serialization-and-interprocess-communication-ipc) for stream framing and the end-of-stream marker.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
