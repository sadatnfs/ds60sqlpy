# rust-033: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-033_solution.rs](rust-033_solution.rs). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Poll a ready computation:** A no-op waker is sufficient only because this fixture cannot require a later external wakeup. The immediately ready future yields seven on its first poll.

**Observe pending without spinning:** The program stops after one inspection rather than wasting CPU pretending a tight loop is a runtime. The pending future reports no completed value.

## Task answers

### Task 1: Predict and explain

Separate future creation, polling and completion.

No separate reference answer has been written for this task. Example A is the evidence to compare with: A no-op waker is sufficient only because this fixture cannot require a later external wakeup. The immediately ready future yields seven on its first poll.

### Task 2: Guided modification

Compose two immediately ready async values and poll the combined fixture.

No separate reference answer has been written for this task. Start from Example B: The program stops after one inspection rather than wasting CPU pretending a tight loop is a runtime. The pending future reports no completed value.

### Task 3: Independent construction

Explain the ownership responsibilities of an executor in a written event trace.

**Written answer.** One possible trace: (1) the caller creates the future and hands it to the executor, which now owns it and keeps it pinned; (2) the executor polls it with a Context whose Waker it supplies; (3) the future registers that waker with the resource it waits on and returns Pending; (4) the resource calls wake, which only schedules the task again; (5) the executor polls once more, the future returns Ready(value), and the executor drops the future and delivers the value to whoever awaits the task. The executor does none of the future's work itself: it owns the future, polls it only when woken, and must drop it on completion or cancellation.

### Task 4: Diagnose a defect

Diagnose creating a future and expecting it to run without a consumer.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Async is not automatically parallel. A no-op waker cannot drive real asynchronous I/O. Dropping a future does not necessarily reverse effects already performed by external systems.

### Task 5: Boundary evidence

Contrast Ready, Pending and dropping an uncompleted future.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Poll a ready computation) and Example B (Observe pending without spinning).

### Task 6: Transfer and justify

Plan a separately prepared Tokio service, naming runtime, cancellation, I/O and dependency requirements.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Future**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A Future represents a computation that can make progress when polled. It may return Ready with a result or Pending and arrange a wakeup when progress becomes possible. Creating an async block does not automatically execute it or create a thread. An executor owns polling and scheduling.

Rust's standard library defines Future and task primitives but does not provide a general production async runtime. Tokio and similar ecosystems are separate prepared dependencies, not installed by this pad. This chapter polls immediately ready futures once to reveal the mechanism. It deliberately does not present a busy polling loop as a correct executor for arbitrary I/O.

An async block produces a Future. Pin protects address-sensitive future state from invalid movement while polled. Context carries a Waker. Poll::Ready and Poll::Pending are distinct completion states.

Async is not automatically parallel. A no-op waker cannot drive real asynchronous I/O. Dropping a future does not necessarily reverse effects already performed by external systems.

## Review before continuing

Run the reference and confirm that it prints `rust-033: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
