# rust-045: Bounded batch pipelines and data accounting

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-044`

## Learning objectives

Apply the same accounting to an Arrow batch reader. Then design cancellation and partial-output semantics for a long-running import.

## Purpose and mental model

A data pipeline needs bounds on admitted input, buffered batches, memory and output. Processing one batch at a time can reduce peak memory, but retaining every batch in a result vector defeats that design. A batch size is not a total-job limit, and one variable-width value can still be very large.

Preserve accounting at every boundary: submitted rows, valid rows, rejected rows and output rows should have defined relationships. Filtering changes row count while projection changes columns. Cancellation and partial failure need explicit outcome semantics so an incomplete report is not presented as complete. The fixture demonstrates deterministic batch accounting without a remote source.

## Vocabulary and concepts

**Admission bound:** A limit on work accepted into processing.

**Streaming aggregation:** Updating a summary without retaining all prior records.

**Accounting invariant:** A defined relationship between input and outcome counts.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

Chunking a slice gives bounded views of owned input. An accumulator stores only the required summary. Checked arithmetic and explicit row counters prevent silent overflow or dropped-record accounting.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Batch size alone does not bound total memory or individual value size. A partial result needs an explicit incomplete status. Do not infer complete input consumption from a valid first batch.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Admission bound, Streaming aggregation, Accounting invariant without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
