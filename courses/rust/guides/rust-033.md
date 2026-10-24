# rust-033: Futures, async syntax and executor boundaries

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-032`

## Learning objectives

Explain the ownership responsibilities of an executor in a written event trace. Then plan a separately prepared Tokio service, naming runtime, cancellation, I/O and dependency requirements.

## Purpose and mental model

A Future represents a computation that can make progress when polled. It may return Ready with a result or Pending and arrange a wakeup when progress becomes possible. Creating an async block does not automatically execute it or create a thread. An executor owns polling and scheduling.

Rust's standard library defines Future and task primitives but does not provide a general production async runtime. Tokio and similar ecosystems are separate prepared dependencies, not installed by this pad. This chapter polls immediately ready futures once to reveal the mechanism. It deliberately does not present a busy polling loop as a correct executor for arbitrary I/O.

## Vocabulary and concepts

**Future:** A computation progressed through polling.

**Executor:** The owner scheduling and polling futures.

**Waker:** A notification mechanism requesting another poll when progress may be possible.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

An async block produces a Future. Pin protects address-sensitive future state from invalid movement while polled. Context carries a Waker. Poll::Ready and Poll::Pending are distinct completion states.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Poll a ready computation

A no-op waker is sufficient only because this fixture cannot require a later external wakeup.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::future::Future;
        use std::task::{Context, Poll, Waker};
        let mut future = Box::pin(async { 7 });
        let mut context = Context::from_waker(Waker::noop());
        assert_eq!(future.as_mut().poll(&mut context), Poll::Ready(7));
    }
    println!("rust-033: passed");
    Ok(())
}
```

**Observe:** The immediately ready future yields seven on its first poll.

### Example B: Observe pending without spinning

The program stops after one inspection rather than wasting CPU pretending a tight loop is a runtime.

```rust


fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::future::Future;
        use std::task::{Context, Poll, Waker};
        let mut future = Box::pin(std::future::pending::<i32>());
        let mut context = Context::from_waker(Waker::noop());
        assert_eq!(future.as_mut().poll(&mut context), Poll::Pending);
    }
    println!("rust-033: passed");
    Ok(())
}
```

**Observe:** The pending future reports no completed value.

## Exercises

1. **Predict and explain.** Separate future creation, polling and completion.

2. **Guided modification.** Compose two immediately ready async values and poll the combined fixture.

3. **Independent construction.** Explain the ownership responsibilities of an executor in a written event trace.

4. **Diagnose a defect.** Diagnose creating a future and expecting it to run without a consumer.

5. **Boundary evidence.** Contrast Ready, Pending and dropping an uncompleted future.

6. **Transfer and justify.** Plan a separately prepared Tokio service, naming runtime, cancellation, I/O and dependency requirements.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Async is not automatically parallel. A no-op waker cannot drive real asynchronous I/O. Dropping a future does not necessarily reverse effects already performed by external systems.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Future, Executor, Waker without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/std/future/trait.Future.html). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-033: Futures, async syntax and executor boundaries.
Read courses/rust/guides/rust-033.md and courses/rust/lessons/rust-033.rs. Prerequisites: rust-032.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-033_solution.rs and
courses/rust/solutions/rust-033_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
