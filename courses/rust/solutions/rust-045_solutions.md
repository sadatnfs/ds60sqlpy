# rust-045: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-045_solution.rs](rust-045_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Aggregate bounded chunks:** The summary retains only counters, not a duplicate copy of every processed batch. Three chunks account for five rows and total fifteen.

**Account for rejected rows:** A rejection policy must preserve the denominator needed to interpret the result. Valid zero is retained and every input row is accounted for.

## Task answers

### Task 1: Predict and explain

Trace chunk sizes and cumulative row counts.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The summary retains only counters, not a duplicate copy of every processed batch. Three chunks account for five rows and total fifteen.

### Task 2: Guided modification

Change the chunk size without changing the final result.

No separate reference answer has been written for this task. Start from Example B: A rejection policy must preserve the denominator needed to interpret the result. Valid zero is retained and every input row is accounted for.

### Task 3: Independent construction

Apply the same accounting to an Arrow batch reader.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use arrow::array::{ArrayRef, AsArray, Int32Array};
    use arrow::datatypes::Int32Type;
    use arrow::record_batch::{RecordBatch, RecordBatchIterator};
    use std::sync::Arc;
    let mut batches = Vec::new();
    for chunk in [vec![2, -1], vec![0, 3, -4]] {
        let column: ArrayRef = Arc::new(Int32Array::from(chunk));
        batches.push(RecordBatch::try_from_iter(vec![("qty", column)])?);
    }
    let schema = batches[0].schema();
    let reader = RecordBatchIterator::new(batches.into_iter().map(Ok), schema);
    let (mut rows, mut accepted) = (0, 0);
    for batch in reader {
        let batch = batch?;
        let values = batch.column(0).as_primitive::<Int32Type>();
        rows += values.len();
        accepted += values.iter().flatten().filter(|v| *v >= 0).count();
    }
    assert_eq!((rows, accepted, rows - accepted), (5, 3, 2));
    Ok(())
}
```

**Observe:** Across two batches, 5 rows split into 3 accepted and 2 rejected.

Counting per batch while reading keeps memory bounded, and rows minus accepted gives the rejected count without double counting.

### Task 4: Diagnose a defect

Diagnose collecting all batches before claiming bounded-memory processing.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Batch size alone does not bound total memory or individual value size. A partial result needs an explicit incomplete status. Do not infer complete input consumption from a valid first batch.

### Task 5: Boundary evidence

Test empty input, an all-rejected batch and a partial final batch.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Aggregate bounded chunks) and Example B (Account for rejected rows).

### Task 6: Transfer and justify

Design cancellation and partial-output semantics for a long-running import.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Admission bound**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A data pipeline needs bounds on admitted input, buffered batches, memory and output. Processing one batch at a time can reduce peak memory, but retaining every batch in a result vector defeats that design. A batch size is not a total-job limit, and one variable-width value can still be very large.

Preserve accounting at every boundary: submitted rows, valid rows, rejected rows and output rows should have defined relationships. Filtering changes row count while projection changes columns. Cancellation and partial failure need explicit outcome semantics so an incomplete report is not presented as complete. The fixture demonstrates deterministic batch accounting without a remote source.

Chunking a slice gives bounded views of owned input. An accumulator stores only the required summary. Checked arithmetic and explicit row counters prevent silent overflow or dropped-record accounting.

Batch size alone does not bound total memory or individual value size. A partial result needs an explicit incomplete status. Do not infer complete input consumption from a valid first batch.

## Review before continuing

Run the reference and confirm that it prints `rust-045: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
