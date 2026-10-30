# rust-029: Channels, backpressure and completion

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-028`

## Learning objectives

Build a bounded producer-consumer report pipeline. Then choose blocking, rejection or intentional dropping for a workload and explain producer evidence.

## Purpose and mental model

A channel transfers values between producers and consumers. Sending can move ownership so the receiving side becomes responsible for the value. A bounded synchronous channel limits how much work can wait in memory. Its capacity is an admission policy, not merely a performance tuning number.

A receiver can finish when all senders are dropped and buffered items are drained. Keeping an unused sender clone alive can therefore keep a consumer waiting. Join producers and observe send/receive errors deliberately. Avoid deadlock by ensuring a blocked producer has a consumer that can still run.

## Vocabulary and concepts

**Channel:** An ownership-transfer communication mechanism.

**Backpressure:** A bound limiting admitted work when consumers lag.

**Disconnection:** The state where the opposite channel endpoint no longer exists.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.rs` with pinned Rust 1.99.1, edition 2024, and the prepared Arrow 60 library. `assert!` and `assert_eq!` remain active in normal builds. The fixed pad accepts one source file without arbitrary arguments, interactive input, Cargo manifests or package installation. The main function returns `Result<(), Box<dyn std::error::Error>>` so later examples can propagate errors with `?`; the final `Ok(())` means this fixture completed successfully. Standard library and Arrow examples remain offline after image preparation. Multi-file Cargo and external ecosystem projects have separate explicit preparation workflows.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

sync_channel creates bounded storage. try_send reports immediate full or disconnected states. send may block until capacity exists. Receiver iteration drains until sender ownership ends.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Make full capacity observable

The rejected value remains visible in the error instead of disappearing silently.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        use std::sync::mpsc::{sync_channel, TrySendError};
        let (send, receive) = sync_channel(1);
        send.try_send(4)?;
        assert!(matches!(send.try_send(5), Err(TrySendError::Full(5))));
        assert_eq!(receive.recv()?, 4);
    }
    println!("rust-029: passed");
    Ok(())
}
```

**Observe:** One item is admitted and the next immediate send reports full capacity.

### Example B: Drain before declaring completion

Producer lifetime and channel completion are explicitly connected.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    {
        let (send, receive) = std::sync::mpsc::sync_channel(2);
        let worker = std::thread::spawn(move || {
            send.send(2).unwrap();
            send.send(3).unwrap();
        });
        let total: i32 = receive.iter().sum();
        worker.join().unwrap();
        assert_eq!(total, 5);
    }
    println!("rust-029: passed");
    Ok(())
}
```

**Observe:** The receiver drains both values and ends after the sender is dropped.

## Exercises

1. **Predict and explain.** Trace queue occupancy and ownership after each send.

2. **Guided modification.** Increase capacity and predict the accepted immediate sends.

3. **Independent construction.** Build a bounded producer-consumer report pipeline.

4. **Diagnose a defect.** Diagnose a receiver waiting because an unused sender clone remains alive.

5. **Boundary evidence.** Test no messages and a disconnected receiver.

6. **Transfer and justify.** Choose blocking, rejection or intentional dropping for a workload and explain producer evidence.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Joining a producer before draining a full bounded channel can deadlock. Ignoring a failed send loses work. Channel capacity does not bound work already started outside the channel.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Channel, Backpressure, Disconnection without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://doc.rust-lang.org/book/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for rust-029: Channels, backpressure and completion.
Read courses/rust/guides/rust-029.md and courses/rust/lessons/rust-029.rs. Prerequisites: rust-028.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/rust/solutions/rust-029_solution.rs and
courses/rust/solutions/rust-029_solutions.md closed until I request comparison or show an attempt.
Use rust-stable for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
