# rust-045: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-045_solution.rs](rust-045_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Aggregate bounded chunks:** The summary retains only counters, not a duplicate copy of every processed batch. Three chunks account for five rows and total fifteen.

**Account for rejected rows:** A rejection policy must preserve the denominator needed to interpret the result. Valid zero is retained and every input row is accounted for.

## Task answers

### Task 1: Predict and explain

Trace chunk sizes and cumulative row counts.

**Written answer.** `values.chunks(2)` over five values yields three chunks: [1, 2], [3, 4] and [5]. After the first chunk `rows` is 2 and `total` is 3; after the second, 4 and 10; after the third, which is partial, 5 and 15. Only the two counters survive between chunks.

**Why it is correct.** Each step adds the chunk's own length and sum, so the final counters equal the totals of the whole input whatever the chunk boundaries are.

**Plausible wrong approach.** Assuming every chunk has two rows predicts six rows after three chunks; the last chunk has only the one remaining value.

**How to verify.** Print `batch.len()` and the running counters inside the loop: 2, 2, 1 and (2, 3), (4, 10), (5, 15).

### Task 2: Guided modification

Change the chunk size without changing the final result.

**Reference answer.** The same statements run as the `Task 2` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let values = [1_i32, 2, 3, 4, 5];
    let mut results = Vec::new();
    for size in 1..=6 {
        let mut rows = 0;
        let mut total = 0;
        let mut chunks = 0;
        for batch in values.chunks(size) {
            chunks += 1;
            rows += batch.len();
            total += batch.iter().sum::<i32>();
        }
        assert_eq!(chunks, values.len().div_ceil(size));
        results.push((rows, total));
    }
    assert!(results.iter().all(|result| *result == (5, 15)));
    Ok(())
}
```

**Observe:** Every chunk size from 1 to 6 gives 5 rows and a total of 15, while the number of chunks follows the ceiling of 5 divided by the size.

Chunk size changes how many steps run and how large each step is, never which values are counted. Testing sizes larger than the input, here 6, covers a single partial chunk too.

**Plausible wrong approach.** Computing the chunk count as `values.len() / size` misses the partial final chunk; for size 2 it predicts 2 chunks, not 3.

**How to verify.** Run the block. Replace `div_ceil(size)` with `/ size` and the assertion fails at size 2.

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

**Written answer.** The defect is `let batches: Vec<RecordBatch> = reader.collect::<Result<_, _>>()?;` followed by the accounting loop, in a pipeline described as bounded-memory. Collecting keeps every batch alive at once, so peak memory grows with the whole input, and the batch size only controls how it is cut up. Process each batch inside `for batch in reader`, keep only counters, and drop the batch at the end of the iteration, as task 3 does.

**Why it is correct.** Bounded memory depends on how much data is alive at the same time. Streaming holds one batch at a time; collecting holds all of them, so the claim is only true for the first design.

**Plausible wrong approach.** Reducing the batch size while still collecting makes each batch smaller but keeps every row in memory.

**How to verify.** Count live batches: a counter incremented on creation and decremented on drop peaks at 1 while streaming and at the number of batches when collecting.

### Task 5: Boundary evidence

Test empty input, an all-rejected batch and a partial final batch.

**Reference answer.** The same statements run as the `Task 5` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn account(values: &[i32], size: usize) -> (usize, usize, usize) {
        let (mut rows, mut accepted) = (0, 0);
        for batch in values.chunks(size) {
            rows += batch.len();
            accepted += batch.iter().filter(|value| **value >= 0).count();
        }
        (rows, accepted, rows - accepted)
    }
    assert_eq!(account(&[], 2), (0, 0, 0));
    assert_eq!(account(&[-1, -2], 2), (2, 0, 2));
    assert_eq!(account(&[1, 2, 3, -4, 0], 2), (5, 4, 1));
    assert_eq!([1, 2, 3, -4, 0].chunks(2).last(), Some(&[0][..]));
    Ok(())
}
```

**Observe:** Empty input gives (0, 0, 0), an all-rejected batch gives two rows with zero accepted, and five values in chunks of two end with the partial batch [0], which is still accepted.

Every case keeps rows equal to accepted plus rejected. The empty case shows the counters start correctly, the all-rejected case shows rejection is counted rather than dropped, and the partial final batch shows the last short chunk is processed.

**Plausible wrong approach.** Skipping a batch that produced no accepted rows also skips its rejected rows, so the all-rejected case would report (0, 0, 0).

**How to verify.** Run the block. Add `if batch.len() < size { continue; }` inside the loop and the partial-batch case loses its final 0.

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
