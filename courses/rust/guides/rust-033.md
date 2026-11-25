# rust-033: Futures, async syntax and executor boundaries

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `rust-032`

## Learning objectives

Explain how futures are polled and woken and what an executor owns. The central exercise is task 3: Explain the ownership responsibilities of an executor in a written event trace.

## Purpose and mental model

A Future represents a computation that can make progress when polled. It may return Ready with a result or Pending and arrange a wakeup when progress becomes possible. Creating an async block does not automatically execute it or create a thread. An executor owns polling and scheduling.

Rust's standard library defines Future and task primitives but does not provide a general production async runtime. Tokio and similar ecosystems are separate prepared dependencies, not installed by this pad. This chapter polls immediately ready futures once to reveal the mechanism. It deliberately does not present a busy polling loop as a correct executor for arbitrary I/O.

## Vocabulary and concepts

**Future:** A computation progressed through polling.

**Executor:** The owner scheduling and polling futures.

**Waker:** A notification mechanism requesting another poll when progress may be possible.

## How to run this lesson

Beyond the prelude, this lesson's programs use `std::future` and `std::task`. A passing run prints `rust-033: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

An async block produces a Future. Pin protects address-sensitive future state from invalid movement while polled. Context carries a Waker. Poll::Ready and Poll::Pending are distinct completion states.

**Reading Example A (Poll a ready computation, code below).** `Box::pin(async { 7 })` creates a future from an async block and pins it on the heap. An async block does nothing when created; its body runs only when something polls it. Pinning is required because `Future::poll` takes `self: Pin<&mut Self>`, a guarantee that the future will not move in memory once polling has started. `Waker::noop()` returns a waker that does nothing when woken, and `Context::from_waker` wraps it in the context that `poll` requires; a real executor would supply a waker that reschedules the task. `future.as_mut()` produces a fresh `Pin<&mut _>` for this call without giving up the box. Because the block contains no `.await`, the first poll runs it to completion and returns `Poll::Ready`.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

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

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Async is not automatically parallel. A no-op waker cannot drive real asynchronous I/O. Dropping a future does not necessarily reverse effects already performed by external systems.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Poll a ready computation) before changing anything, and confirm its observation: The immediately ready future yields seven on its first poll.
2. Compare Example B (Observe pending without spinning) with Example A and name the first line whose behavior differs. Its observation is: The pending future reports no completed value.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Async is not automatically parallel.

Tempting approaches to rule out before you compare:

- **Task 1.** Thinking `async { 7 }` evaluates 7 at creation predicts side effects before any poll. Put a `println!` inside the block and nothing prints until the poll.
- **Task 2.** Expecting the two inner futures to run in parallel misreads `.await`: inside one async block they run sequentially, and neither runs at all until `combined` is polled.
- **Task 5.** Expecting `finished` in the log assumes a dropped future runs to the end in the background. Nothing polls it after `drop`, so its remaining code is discarded.

## Self-check and next step

What does `async { 7 }` produce before anything polls it, and why does its first poll return `Poll::Ready(7)`? Why does `std::future::pending` return `Poll::Pending` on every poll, and what would a loop that kept polling it do to a CPU core? Why is `Waker::noop()` enough for these two checks but not for a future waiting on real I/O?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [the `Future` trait documentation](https://doc.rust-lang.org/std/future/trait.Future.html) for `poll`, `Poll::Pending` and the waker contract.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
