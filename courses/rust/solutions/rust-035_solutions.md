# rust-035: explanation and comparison

Executable reference: [rust-035_solution.rs](rust-035_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Distinguish handle size from owned data:** Inline size is not a total retained-memory measurement. String handle size is equal while the owned text lengths differ.

**Prepare capacity without inventing elements:** Reserved capacity is a resource decision, not part of the logical dataset. Only ten initialized elements participate in the sum.

## Task answers

### Task 1: Predict and explain

Separate inline handles from their owned allocations.

**Written answer.** `small` and `large` are both `String` handles: a pointer, a capacity and a length, which is 24 bytes on a 64-bit target, so `size_of_val` reports the same number for both. The text lives in separate heap buffers owned by each handle, about 1 byte for `small` and 1000 bytes for `large`.

**Why it is correct.** `size_of_val` measures only the inline value. Heap data reached through a pointer is owned by the value but is not part of its inline size.

**Plausible wrong approach.** Concluding that the two strings use the same memory because the sizes match ignores the heap buffers entirely.

**How to verify.** Assert `std::mem::size_of::<String>() == 3 * std::mem::size_of::<usize>()` and compare `small.capacity()` with `large.capacity()`.

### Task 2: Guided modification

Compare vector lengths after different reserve calls.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 2` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut exact: Vec<i32> = Vec::new();
    exact.reserve_exact(10);
    let mut loose: Vec<i32> = Vec::new();
    loose.reserve(10);
    assert_eq!((exact.len(), loose.len()), (0, 0));
    assert!(exact.capacity() >= 10 && loose.capacity() >= 10);
    exact.extend(0..10);
    loose.extend(0..10);
    assert_eq!(exact, loose);
    let before = exact.capacity();
    exact.reserve(0);
    assert_eq!(exact.capacity(), before);
    Ok(())
}
```

**Observe:** Both reserve calls leave the length at 0 while giving at least 10 slots of capacity; after the same ten pushes the two vectors are equal, and reserving 0 more changes nothing.

`reserve` may round capacity up for future growth, and `reserve_exact` asks for no extra, but neither creates elements. Length counts initialized values, which is what equality and iteration see; capacity is only allocation.

**Plausible wrong approach.** Asserting `exact.capacity() == 10` relies on an allocator detail that the documentation does not promise; only `>= 10` is guaranteed.

**How to verify.** Run the block. Then add `assert_eq!(exact[0], 0);` right after `reserve_exact` and the index panics, because no element exists yet.

### Task 3: Independent construction

Write a benchmark plan comparing repeated clone with borrowed processing.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 3` block.

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

**Written answer.** The defect is reporting `std::mem::size_of_val(&rows)` for `rows: Vec<String>` as the memory the rows retain. It is 24 bytes whether `rows` holds zero strings or a million, because it counts only the `Vec` handle. Retained memory also includes the buffer of `capacity * size_of::<String>()` bytes and each string's own heap capacity.

**Why it is correct.** Nested owners each hold their own allocations behind pointers. An inline size can never see them, so an estimate must walk the structure or measure at the allocator.

**Plausible wrong approach.** Switching to `size_of_val(&rows[..])` counts the `String` handles in the buffer but still misses every string's text.

**How to verify.** Assert that `size_of_val` of a vector of 1000 long strings equals `size_of_val(&Vec::<String>::new())`, then sum `capacity()` over the strings to see the missing part.

### Task 5: Boundary evidence

Test empty and large inputs with the same correctness oracle.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 5` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    fn checksum_fast(values: &[u32]) -> u64 {
        values.iter().map(|&value| u64::from(value)).sum()
    }
    fn checksum_oracle(values: &[u32]) -> u64 {
        let mut total = 0_u64;
        for value in values {
            total += u64::from(*value);
        }
        total
    }
    let empty: Vec<u32> = Vec::new();
    let large = vec![u32::MAX; 100_000];
    for input in [&empty[..], &[7][..], &large[..]] {
        assert_eq!(checksum_fast(input), checksum_oracle(input));
    }
    assert_eq!(checksum_fast(&empty), 0);
    assert_eq!(checksum_fast(&large), 100_000 * u64::from(u32::MAX));
    Ok(())
}
```

**Observe:** The empty, single-value and 100,000-value inputs agree between both implementations, with 0 for empty and 429,496,729,500,000 for the large input.

The same oracle judges every input size, so a faster version cannot win by changing semantics. Widening to `u64` before adding keeps the large case exact; the large input is where a `u32` accumulator would overflow.

**Plausible wrong approach.** Testing only the large input for speed and the small input for correctness lets a version that overflows on large data pass both checks.

**How to verify.** Run the block. Change `checksum_fast` to `values.iter().sum::<u32>() as u64` and the large case panics with attempt to add with overflow.

### Task 6: Transfer and justify

Choose a layout for repeated column scans and explain locality, ownership and update tradeoffs.

**Judging criteria.** A strong answer stores each scanned field in its own contiguous `Vec`, a structure of arrays, so a scan reads only the bytes it needs, instead of a `Vec` of row structs or of boxed rows. It states who owns the columns, how a row update must touch several vectors and keep their lengths equal, and what growth costs when a column's capacity is exceeded. It supports the choice with a measurement on the same data. State one limitation: inserting or updating whole rows becomes more awkward and error-prone than with one struct per row.

## Mechanism and diagnostic reasoning

Rust exposes enough control to optimize data layout and allocation, but correctness and a workload model come first. Contiguous arrays can improve locality for column scans, while pointer-heavy structures may incur indirection. Copying a small value can be cheaper than managing shared ownership; cloning a large buffer can dominate a pipeline.

Measure allocations and throughput under a realistic workload, and retain identical semantics across implementations. A single elapsed-time sample is weak evidence. The classroom uses deterministic size and operation observations, then prepares the learner to design an external benchmark. Representation details should not leak into a stable API unless the contract requires them.

size_of measures a type's inline representation, not every allocation reachable from it. Vec capacity is separate allocated storage. reserve can reduce reallocations without changing the algorithmic cost of shifting or sorting.

Benchmarking different validation or ordering semantics is invalid. Size and alignment can vary by target. Do not use unsafe layout assumptions to replace an actual profiling result.

## Review before continuing

Rebuild Example B (Prepare capacity without inventing elements) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
