# rust-035: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-035_solution.rs](rust-035_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Distinguish handle size from owned data:** Inline size is not a total retained-memory measurement. String handle size is equal while the owned text lengths differ.

**Prepare capacity without inventing elements:** Reserved capacity is a resource decision, not part of the logical dataset. Only ten initialized elements participate in the sum.

## Task answers

### Task 1: Predict and explain

Separate inline handles from their owned allocations.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Inline size is not a total retained-memory measurement. String handle size is equal while the owned text lengths differ.

### Task 2: Guided modification

Compare vector lengths after different reserve calls.

No separate reference answer has been written for this task. Start from Example B: Reserved capacity is a resource decision, not part of the logical dataset. Only ten initialized elements participate in the sum.

### Task 3: Independent construction

Write a benchmark plan comparing repeated clone with borrowed processing.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn total_cloned(rows: &[String]) -> usize {
        rows.iter().map(|row| row.clone().len()).sum()
    }
    fn total_borrowed(rows: &[String]) -> usize {
        rows.iter().map(|row| row.len()).sum()
    }
    let rows: Vec<String> = (0..100).map(|i| format!("row-{i}")).collect();
    assert_eq!(total_cloned(&rows), total_borrowed(&rows));
    Ok(())
}
```

**Observe:** Both versions return the same total, so a benchmark compares only their cost.

Plan: first prove the two versions agree, as this check does; then time both in a release build at several input sizes (100, 10,000 and 1,000,000 rows) after a warm-up, repeat each measurement, and report the median and spread together with allocation counts. One run on one machine is not a general performance claim.

### Task 4: Diagnose a defect

Diagnose measuring size_of as total memory retained by nested objects.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Benchmarking different validation or ordering semantics is invalid. Size and alignment can vary by target. Do not use unsafe layout assumptions to replace an actual profiling result.

### Task 5: Boundary evidence

Test empty and large inputs with the same correctness oracle.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Distinguish handle size from owned data) and Example B (Prepare capacity without inventing elements).

### Task 6: Transfer and justify

Choose a layout for repeated column scans and explain locality, ownership and update tradeoffs.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Inline size**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Rust exposes enough control to optimize data layout and allocation, but correctness and a workload model come first. Contiguous arrays can improve locality for column scans, while pointer-heavy structures may incur indirection. Copying a small value can be cheaper than managing shared ownership; cloning a large buffer can dominate a pipeline.

Measure allocations and throughput under a realistic workload, and retain identical semantics across implementations. A single elapsed-time sample is weak evidence. The classroom uses deterministic size and operation observations, then prepares the learner to design an external benchmark. Representation details should not leak into a stable API unless the contract requires them.

size_of measures a type's inline representation, not every allocation reachable from it. Vec capacity is separate allocated storage. reserve can reduce reallocations without changing the algorithmic cost of shifting or sorting.

Benchmarking different validation or ordering semantics is invalid. Size and alignment can vary by target. Do not use unsafe layout assumptions to replace an actual profiling result.

## Review before continuing

Run the reference and confirm that it prints `rust-035: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
