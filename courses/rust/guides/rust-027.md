# rust-027: Scoped threads and explicit joins

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-026`

## Learning objectives

Build a scoped parallel computation returning values to the parent. Then choose threads or sequential work using workload size and synchronization cost.

## Purpose and mental model

A thread can run concurrently with its creator and must have a clear lifetime owner. Unscoped thread spawn requires captured references to satisfy the required lifetime, often leading to owned move captures. Scoped threads instead guarantee joining before the scope returns, allowing safe borrowing of suitable local data.

Joining observes completion and panic outcomes. Do not infer completion from a sleep. Independent tasks can compute values and return them to one owner, avoiding shared mutable state. Threads are an execution mechanism, not an automatic speedup for tiny workloads or blocked external systems.

## Vocabulary and concepts

**Thread:** An independently scheduled execution context.

**Join:** Waiting for and observing a thread outcome.

**Scoped thread:** A thread whose lifetime is bounded by its enclosing scope.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

std::thread::scope bounds child lifetimes. scope.spawn creates a scoped worker. join returns its result or panic information. Immutable borrowed inputs can be shared when their types satisfy the concurrency requirements.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Borrow local input safely

The scope guarantees the worker cannot outlive the owner of the borrowed vector.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let values = vec![2, 3, 4];
        let total = std::thread::scope(|scope| {
            let handle = scope.spawn(|| values.iter().sum::<i32>());
            handle.join().expect("fixture worker")
        });
        assert_eq!(total, 9);
        assert_eq!(values.len(), 3);
    }
    println!("rust-027: passed");
    Ok(())
}
```

**Observe:** The borrowed input remains usable after the joined scope.

### Example B: Return independent results

No shared writable accumulator is needed for this decomposition.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let total = std::thread::scope(|scope| {
            let left = scope.spawn(|| 2 + 3);
            let right = scope.spawn(|| 4 + 5);
            left.join().unwrap() + right.join().unwrap()
        });
        assert_eq!(total, 14);
    }
    println!("rust-027: passed");
    Ok(())
}
```

**Observe:** The parent combines two completed results.

## Exercises

1. **Predict and explain.** Identify who owns input and each thread handle.

2. **Guided modification.** Split an array into two borrowed halves and combine their totals.

3. **Independent construction.** Build a scoped parallel computation returning values to the parent.

4. **Diagnose a defect.** Diagnose dropping a handle and assuming the work finished.

5. **Boundary evidence.** Test empty partitions and an intentional worker panic in a controlled external test.

6. **Transfer and justify.** Choose threads or sequential work using workload size and synchronization cost.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Sleep is not a synchronization guarantee. A joined panic is a distinct failure that should not become a default successful result. More threads can increase overhead and resource pressure.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Thread, Join, Scoped thread without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-027: Scoped threads and explicit joins.
Read courses/rust/guides/rust-027.md and courses/rust/lessons/rust-027.rs. Prerequisites: rust-026.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-027_solution.rs and
courses/rust/solutions/rust-027_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
