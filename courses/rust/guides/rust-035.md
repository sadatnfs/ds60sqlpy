# rust-035: Memory layout, allocation and performance evidence

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-034`

## Learning objectives

Write a benchmark plan comparing repeated clone with borrowed processing. Then choose a layout for repeated column scans and explain locality, ownership and update tradeoffs.

## Purpose and mental model

Rust exposes enough control to optimize data layout and allocation, but correctness and a workload model come first. Contiguous arrays can improve locality for column scans, while pointer-heavy structures may incur indirection. Copying a small value can be cheaper than managing shared ownership; cloning a large buffer can dominate a pipeline.

Measure allocations and throughput under a realistic workload, and retain identical semantics across implementations. A single elapsed-time sample is weak evidence. The classroom uses deterministic size and operation observations, then prepares the learner to design an external benchmark. Representation details should not leak into a stable API unless the contract requires them.

## Vocabulary and concepts

**Inline size:** The bytes occupied directly by a value representation.

**Locality:** Access patterns that reuse nearby memory effectively.

**Allocation profile:** Evidence about the number and size of allocated resources.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

size_of measures a type's inline representation, not every allocation reachable from it. Vec capacity is separate allocated storage. reserve can reduce reallocations without changing the algorithmic cost of shifting or sorting.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Distinguish handle size from owned data

Inline size is not a total retained-memory measurement.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let small = String::from("a");
        let large = "x".repeat(1000);
        assert_eq!(std::mem::size_of_val(&small), std::mem::size_of_val(&large));
        assert_ne!(small.len(), large.len());
    }
    println!("rust-035: passed");
    Ok(())
}
```

**Observe:** String handle size is equal while the owned text lengths differ.

### Example B: Prepare capacity without inventing elements

Reserved capacity is a resource decision, not part of the logical dataset.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let mut values = Vec::with_capacity(100);
        values.extend(0..10);
        assert_eq!(values.len(), 10);
        assert!(values.capacity() >= 100);
        assert_eq!(values.iter().sum::<i32>(), 45);
    }
    println!("rust-035: passed");
    Ok(())
}
```

**Observe:** Only ten initialized elements participate in the sum.

## Exercises

1. **Predict and explain.** Separate inline handles from their owned allocations.

2. **Guided modification.** Compare vector lengths after different reserve calls.

3. **Independent construction.** Write a benchmark plan comparing repeated clone with borrowed processing.

4. **Diagnose a defect.** Diagnose measuring size_of as total memory retained by nested objects.

5. **Boundary evidence.** Test empty and large inputs with the same correctness oracle.

6. **Transfer and justify.** Choose a layout for repeated column scans and explain locality, ownership and update tradeoffs.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Benchmarking different validation or ordering semantics is invalid. Size and alignment can vary by target. Do not use unsafe layout assumptions to replace an actual profiling result.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Inline size, Locality, Allocation profile without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-035: Memory layout, allocation and performance evidence.
Read courses/rust/guides/rust-035.md and courses/rust/lessons/rust-035.rs. Prerequisites: rust-034.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-035_solution.rs and
courses/rust/solutions/rust-035_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
