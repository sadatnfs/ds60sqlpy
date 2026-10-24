# rust-033: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-033_solution.rs](rust-033_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Poll a ready computation:** A no-op waker is sufficient only because this fixture cannot require a later external wakeup. The immediately ready future yields seven on its first poll.

**Observe pending without spinning:** The program stops after one inspection rather than wasting CPU pretending a tight loop is a runtime. The pending future reports no completed value.

## Reason through the six tasks

1. **Predict and explain.** Separate future creation, polling and completion.

2. **Guided modification.** Compose two immediately ready async values and poll the combined fixture.

3. **Independent construction.** Explain the ownership responsibilities of an executor in a written event trace.

4. **Diagnose a defect.** Diagnose creating a future and expecting it to run without a consumer.

5. **Boundary evidence.** Contrast Ready, Pending and dropping an uncompleted future.

6. **Transfer and justify.** Plan a separately prepared Tokio service, naming runtime, cancellation, I/O and dependency requirements.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A Future represents a computation that can make progress when polled. It may return Ready with a result or Pending and arrange a wakeup when progress becomes possible. Creating an async block does not automatically execute it or create a thread. An executor owns polling and scheduling.

Rust's standard library defines Future and task primitives but does not provide a general production async runtime. Tokio and similar ecosystems are separate prepared dependencies, not installed by this pad. This chapter polls immediately ready futures once to reveal the mechanism. It deliberately does not present a busy polling loop as a correct executor for arbitrary I/O.

An async block produces a Future. Pin protects address-sensitive future state from invalid movement while polled. Context carries a Waker. Poll::Ready and Poll::Pending are distinct completion states.

Async is not automatically parallel. A no-op waker cannot drive real asynchronous I/O. Dropping a future does not necessarily reverse effects already performed by external systems.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
