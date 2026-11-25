# rust-045: Bounded batch pipelines and data accounting

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-044`

## Learning objectives

Process data in bounded batches while accounting for every accepted and rejected row. The central exercise is task 3: Apply the same accounting to an Arrow batch reader.

## Purpose and mental model

A data pipeline needs bounds on admitted input, buffered batches, memory and output. Processing one batch at a time can reduce peak memory, but retaining every batch in a result vector defeats that design. A batch size is not a total-job limit, and one variable-width value can still be very large.

Preserve accounting at every boundary: submitted rows, valid rows, rejected rows and output rows should have defined relationships. Filtering changes row count while projection changes columns. Cancellation and partial failure need explicit outcome semantics so an incomplete report is not presented as complete. The fixture demonstrates deterministic batch accounting without a remote source.

## Vocabulary and concepts

**Admission bound:** A limit on work accepted into processing.

**Streaming aggregation:** Updating a summary without retaining all prior records.

**Accounting invariant:** A defined relationship between input and outcome counts.

## How to run this lesson

This lesson's programs need only the prelude and their own helpers. A passing run prints `rust-045: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

Chunking a slice gives bounded views of owned input. An accumulator stores only the required summary. Checked arithmetic and explicit row counters prevent silent overflow or dropped-record accounting.

**Reading Example A (Aggregate bounded chunks, code below).** `values.chunks(2)` returns an iterator of slices, each at most two elements long, borrowed from the array in order without copying. Every element appears in exactly one chunk, and only the final chunk may be shorter than the requested size; the method panics if the size is 0. Inside the loop, `batch` is a `&[i32]`. `batch.len()` adds the chunk's row count to `rows`, and `batch.iter().sum::<i32>()` adds its values to `total`, with the turbofish naming the sum type. The loop holds one chunk at a time, so its working memory does not grow with the input. The final assertion compares the tuple `(rows, total)` in one step, checking that the accounting saw every row and every value.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

## Worked example / walkthrough

### Example A: Aggregate bounded chunks

The summary retains only counters, not a duplicate copy of every processed batch.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = [1_i32, 2, 3, 4, 5];
        let mut total = 0;
        let mut rows = 0;
        for batch in values.chunks(2) {
            rows += batch.len();
            total += batch.iter().sum::<i32>();
        }
        assert_eq!((rows, total), (5, 15));
    }
    println!("rust-045: passed");
    Ok(())
}
```

**Observe:** Three chunks account for five rows and total fifteen.

### Example B: Account for rejected rows

A rejection policy must preserve the denominator needed to interpret the result.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = [2, -1, 0, 3];
        let accepted: Vec<_> = values.iter().copied().filter(|value| *value >= 0).collect();
        let rejected = values.len() - accepted.len();
        assert_eq!(accepted, vec![2, 0, 3]);
        assert_eq!(accepted.len() + rejected, values.len());
    }
    println!("rust-045: passed");
    Ok(())
}
```

**Observe:** Valid zero is retained and every input row is accounted for.

## Exercises

1. **Predict and explain.** Trace chunk sizes and cumulative row counts.

2. **Guided modification.** Change the chunk size without changing the final result.

3. **Independent construction.** Apply the same accounting to an Arrow batch reader.

4. **Diagnose a defect.** Diagnose collecting all batches before claiming bounded-memory processing.

5. **Boundary evidence.** Test empty input, an all-rejected batch and a partial final batch.

6. **Transfer and justify.** Design cancellation and partial-output semantics for a long-running import.

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Batch size alone does not bound total memory or individual value size. A partial result needs an explicit incomplete status. Do not infer complete input consumption from a valid first batch.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Aggregate bounded chunks) before changing anything, and confirm its observation: Three chunks account for five rows and total fifteen.
2. Compare Example B (Account for rejected rows) with Example A and name the first line whose behavior differs. Its observation is: Valid zero is retained and every input row is accounted for.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Batch size alone does not bound total memory or individual value size.

Tempting approaches to rule out before you compare:

- **Task 1.** Assuming every chunk has two rows predicts six rows after three chunks; the last chunk has only the one remaining value.
- **Task 2.** Computing the chunk count as `values.len() / size` misses the partial final chunk; for size 2 it predicts 2 chunks, not 3.
- **Task 5.** Skipping a batch that produced no accepted rows also skips its rejected rows, so the all-rejected case would report (0, 0, 0).

## Self-check and next step

Why does `chunks(2)` over Example A's five values produce three batches, and how long is the last one? What bounds memory in a chunked pipeline: the chunk size, the number of chunks or both? State Example B's accounting invariant in words, and name the rows a pipeline that silently skipped rejects would make disappear.

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the `slice::chunks` documentation](https://doc.rust-lang.org/std/primitive.slice.html#method.chunks) for why the last chunk may be shorter than the rest.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-045: Bounded batch pipelines and data accounting.
Read courses/rust/guides/rust-045.md and courses/rust/lessons/rust-045.rs. Prerequisites: rust-044.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-045_solution.rs and
courses/rust/solutions/rust-045_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
