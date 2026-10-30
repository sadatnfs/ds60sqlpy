# rust-030: Send, Sync and type-driven concurrency safety

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-029`

## Learning objectives

Choose a safe shared-state type for a small concurrent counter. Then document why a proposed custom type is or is not Send and Sync from its members.

## Purpose and mental model

Send describes whether ownership of a value can cross thread boundaries. Sync describes whether shared references can be safely used across threads, with the relationship that a shared reference to T is Send when T is Sync. These marker traits express safety properties, not performance or automatic synchronization.

Rc is single-threaded shared ownership; Arc supports concurrent reference counts. Interior-mutability types have different synchronization rules. The compiler rejects unsafe combinations, but user-defined unsafe implementations can bypass that protection only under a rigorous invariant. Prefer composing known safe types before declaring manual marker implementations.

## Vocabulary and concepts

**Send:** A marker permitting ownership transfer across threads.

**Sync:** A marker permitting safe shared-reference access across threads.

**Marker trait:** A trait expressing a property without ordinary callable methods.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

A generic bound `T: Send` requires cross-thread transfer capability. `T: Sync` requires safe shared access. Thread spawn also imposes a lifetime requirement; Send and static solve different constraints.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Transfer owned data

String's ownership and Send contract make the transfer valid without shared mutation.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let text = String::from("owned");
        let worker = std::thread::spawn(move || text.len());
        assert_eq!(worker.join().unwrap(), 5);
    }
    println!("rust-030: passed");
    Ok(())
}
```

**Observe:** Owned text crosses the thread boundary and returns its length.

### Example B: Check capabilities at compile time

Compile-time capability evidence is different from a runtime stress test.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        fn require_send<T: Send>() {}
        fn require_sync<T: Sync>() {}
        require_send::<String>();
        require_sync::<String>();
        require_send::<std::sync::Arc<std::sync::Mutex<i32>>>();
        assert_eq!(std::sync::Arc::strong_count(&std::sync::Arc::new(1)), 1);
    }
    println!("rust-030: passed");
    Ok(())
}
```

**Observe:** The compiler accepts the declared safe capability combinations.

## Exercises

1. **Predict and explain.** Separate ownership transfer from shared access.

2. **Guided modification.** Move a Vec into a worker and return a derived value.

3. **Independent construction.** Choose a safe shared-state type for a small concurrent counter.

4. **Diagnose a defect.** Try sending Rc across threads and explain the diagnostic rather than adding unsafe.

5. **Boundary evidence.** Test a scoped borrowed input and compare its lifetime requirement with spawn.

6. **Transfer and justify.** Document why a proposed custom type is or is not Send and Sync from its members.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Send does not mean simultaneous mutation is safe. Static does not mean allocated forever; it constrains borrowed references in the value. Never add unsafe impl solely to silence a compiler error.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Send, Sync, Marker trait without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-030: Send, Sync and type-driven concurrency safety.
Read courses/rust/guides/rust-030.md and courses/rust/lessons/rust-030.rs. Prerequisites: rust-029.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-030_solution.rs and
courses/rust/solutions/rust-030_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
