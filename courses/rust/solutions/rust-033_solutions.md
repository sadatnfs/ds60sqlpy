# rust-033: explanation and comparison

Executable reference: [rust-033_solution.rs](rust-033_solution.rs), which runs both examples and the coded answers.

Open this only after [an attempt](../STUDY-GUIDE.md#attempt-a-lesson).

## Why the two examples differ

**Poll a ready computation:** A no-op waker is sufficient only because this fixture cannot require a later external wakeup. The immediately ready future yields seven on its first poll.

**Observe pending without spinning:** The program stops after one inspection rather than wasting CPU pretending a tight loop is a runtime. The pending future reports no completed value.

## Task answers

### Task 1: Predict and explain

Separate future creation, polling and completion.

**Written answer.** `async { 7 }` creates a future value and runs none of its body. `Box::pin` gives it a stable address, which `poll` requires. The single `poll` call runs the body; because nothing inside waits, it finishes and returns `Poll::Ready(7)`, which is completion. In Example B, `pending()` returns `Poll::Pending` on every poll and never completes.

**Why it is correct.** A future is a state machine that advances only when something polls it. Creation, each poll and completion are separate events, and only an executor (or this one-poll fixture) causes the middle one.

**Plausible wrong approach.** Thinking `async { 7 }` evaluates 7 at creation predicts side effects before any poll. Put a `println!` inside the block and nothing prints until the poll.

**How to verify.** Add `let mut flag = false; let mut probe = Box::pin(async { flag = true; });` and check that `flag` changes only after `probe.as_mut().poll(&mut context)`.

### Task 2: Guided modification

Compose two immediately ready async values and poll the combined fixture.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 2` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use std::future::Future;
    use std::task::{Context, Poll, Waker};
    let left = async { 3 };
    let right = async { 4 };
    let mut combined = Box::pin(async { left.await + right.await });
    let mut context = Context::from_waker(Waker::noop());
    assert_eq!(combined.as_mut().poll(&mut context), Poll::Ready(7));
    Ok(())
}
```

**Observe:** One poll of the combined future returns Ready(7).

`combined` owns `left` and `right` and awaits them one after the other. Both are immediately ready, so a single poll drives all three futures to completion. With a future that could return `Pending`, the same poll would stop at that `.await` and report `Pending`.

**Plausible wrong approach.** Expecting the two inner futures to run in parallel misreads `.await`: inside one async block they run sequentially, and neither runs at all until `combined` is polled.

**How to verify.** Run the block. Replace `right` with `std::future::pending::<i32>()` and the poll returns `Poll::Pending`.

### Task 3: Independent construction

Explain the ownership responsibilities of an executor in a written event trace.

**Written answer.** One possible trace: (1) the caller creates the future and hands it to the executor, which now owns it and keeps it pinned; (2) the executor polls it with a Context whose Waker it supplies; (3) the future registers that waker with the resource it waits on and returns Pending; (4) the resource calls wake, which only schedules the task again; (5) the executor polls once more, the future returns Ready(value), and the executor drops the future and delivers the value to whoever awaits the task. The executor does none of the future's work itself: it owns the future, polls it only when woken, and must drop it on completion or cancellation.

### Task 4: Diagnose a defect

Diagnose creating a future and expecting it to run without a consumer.

**Written answer.** The defect is calling an async function such as `save_report(rows);` without `.await` or a runtime. The call only builds a future, which is dropped at the semicolon without ever being polled, so no report is written. rustc warns `unused implementer of Future that must be used` and notes that futures do nothing unless you `.await` or poll them.

**Why it is correct.** Rust futures are lazy: work happens only during `poll`. Without a consumer there is no poll, so the program silently skips the operation.

**Plausible wrong approach.** Binding the result, `let _pending = save_report(rows);`, removes the warning but still never polls it, so the report is never written.

**How to verify.** Compile `async fn save() {} fn main() { save(); }` and read the `unused_must_use` warning.

### Task 5: Boundary evidence

Contrast Ready, Pending and dropping an uncompleted future.

**Reference answer**, wrapped in `main`; the reference runs it as its `Task 5` block.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use std::future::Future;
    use std::task::{Context, Poll, Waker};
    struct Note<'a>(&'a std::cell::RefCell<Vec<&'static str>>);
    impl Drop for Note<'_> {
        fn drop(&mut self) {
            self.0.borrow_mut().push("dropped");
        }
    }
    let mut context = Context::from_waker(Waker::noop());
    let mut ready = Box::pin(async { 1 });
    assert_eq!(ready.as_mut().poll(&mut context), Poll::Ready(1));
    let mut waiting = Box::pin(std::future::pending::<i32>());
    assert_eq!(waiting.as_mut().poll(&mut context), Poll::Pending);
    let log = std::cell::RefCell::new(Vec::new());
    let mut unfinished = Box::pin(async {
        let _note = Note(&log);
        log.borrow_mut().push("started");
        std::future::pending::<()>().await;
        log.borrow_mut().push("finished");
    });
    assert_eq!(unfinished.as_mut().poll(&mut context), Poll::Pending);
    drop(unfinished);
    assert_eq!(*log.borrow(), vec!["started", "dropped"]);
    Ok(())
}
```

**Observe:** The ready future yields Ready(1), the pending one yields Pending, and the unfinished future logs started and then dropped, but never finished.

Dropping a pending future cancels it at its current `.await`: the code after that point never runs, while values the body already created are dropped normally. The log shows both halves, which is why cancellation safety matters when a future has already performed part of its work.

**Plausible wrong approach.** Expecting `finished` in the log assumes a dropped future runs to the end in the background. Nothing polls it after `drop`, so its remaining code is discarded.

**How to verify.** Run the block. Remove `std::future::pending::<()>().await;` and the first poll returns `Ready(())`, with `finished` logged before `dropped`.

### Task 6: Transfer and justify

Plan a separately prepared Tokio service, naming runtime, cancellation, I/O and dependency requirements.

**Judging criteria.** A strong plan names the runtime flavor, multi-threaded or current-thread, and where it is built; how cancellation reaches each task, for example a token checked at every `.await`, and what partial work survives; which I/O uses Tokio's async types instead of blocking `std` calls; and the exact crates and features to prepare, such as `tokio` with `rt-multi-thread`, `net` and `macros`, pinned in `Cargo.lock`. It lives in a separate Cargo project because the pad has no Tokio. State one limitation: a dropped future stops at its last `.await`, so earlier state changes need their own cleanup.

## Mechanism and diagnostic reasoning

A Future represents a computation that can make progress when polled. It may return Ready with a result or Pending and arrange a wakeup when progress becomes possible. Creating an async block does not automatically execute it or create a thread. An executor owns polling and scheduling.

Rust's standard library defines Future and task primitives but does not provide a general production async runtime. Tokio and similar ecosystems are separate prepared dependencies, not installed by this pad. This chapter polls immediately ready futures once to reveal the mechanism. It deliberately does not present a busy polling loop as a correct executor for arbitrary I/O.

An async block produces a Future. Pin protects address-sensitive future state from invalid movement while polled. Context carries a Waker. Poll::Ready and Poll::Pending are distinct completion states.

Async is not automatically parallel. A no-op waker cannot drive real asynchronous I/O. Dropping a future does not necessarily reverse effects already performed by external systems.

## Review before continuing

Rebuild Example B (Observe pending without spinning) from a blank pad.

Review routine: [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).
