# rust-029: Channels, backpressure and completion

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `rust-028`

## Learning objectives

Connect threads with bounded channels and finish pipelines by dropping senders. The central exercise is task 3: Build a bounded producer-consumer report pipeline.

## Purpose and mental model

A channel transfers values between producers and consumers. Sending can move ownership so the receiving side becomes responsible for the value. A bounded synchronous channel limits how much work can wait in memory. Its capacity is an admission policy, not merely a performance tuning number.

A receiver can finish when all senders are dropped and buffered items are drained. Keeping an unused sender clone alive can therefore keep a consumer waiting. Join producers and observe send/receive errors deliberately. Avoid deadlock by ensuring a blocked producer has a consumer that can still run.

## Vocabulary and concepts

**Channel:** An ownership-transfer communication mechanism.

**Backpressure:** A bound limiting admitted work when consumers lag.

**Disconnection:** The state where the opposite channel endpoint no longer exists.

## How to run this lesson

Beyond the prelude, this lesson's programs use `std::sync` and `std::thread`. A passing run prints `rust-029: passed`.

Pad setup and limits: [Run a lesson](../STUDY-GUIDE.md#run-a-lesson).

Before you run anything, follow [Attempt a lesson](../STUDY-GUIDE.md#attempt-a-lesson).



## Syntax anatomy and execution trace

sync_channel creates bounded storage. try_send reports immediate full or disconnected states. send may block until capacity exists. Receiver iteration drains until sender ownership ends.

**Reading Example A (Make full capacity observable, code below).** `sync_channel(1)` creates a bounded channel and returns a pair, a `SyncSender` and a `Receiver`, destructured here as `send` and `receive`. The argument is the buffer capacity. `try_send` never blocks: it returns `Ok(())` when the value fits and an error otherwise, and the `?` on the first call propagates any error out of `main`. The `TrySendError` enum distinguishes `Full`, which hands the rejected value back inside the variant, from `Disconnected`, which means the receiver is gone. `matches!` with the pattern `Err(TrySendError::Full(5))` checks both the variant and the returned value. `recv` blocks until an item is available and returns `Result<T, RecvError>`; its `?` would surface a disconnection.

Method for tracing your own variants: [Trace a program](../STUDY-GUIDE.md#trace-a-program).

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

Record each task as in [Keep evidence for each task](../STUDY-GUIDE.md#keep-evidence-for-each-task).

## Common pitfalls and diagnosis

Joining a producer before draining a full bounded channel can deadlock. Ignoring a failed send loses work. Channel capacity does not bound work already started outside the channel.

To turn a pitfall into a test, see [Design a regression case](../STUDY-GUIDE.md#design-a-regression-case).

## Progressive hints

1. Reproduce Example A (Make full capacity observable) before changing anything, and confirm its observation: One item is admitted and the next immediate send reports full capacity.
2. Compare Example B (Drain before declaring completion) with Example A and name the first line whose behavior differs. Its observation is: The receiver drains both values and ends after the sender is dropped.
3. Before opening the explanation, test your task 3 attempt against this lesson's main pitfall: Joining a producer before draining a full bounded channel can deadlock.

Tempting approaches to rule out before you compare:

- **Task 1.** Expecting `try_send(5)` to wait for space, or to discard 5, misreads the API: `try_send` never blocks, and `Full` hands the value back so the caller decides what to do with it.
- **Task 2.** Predicting capacity plus one, or that `sync_channel(0)` accepts a single item, is wrong: a zero-capacity channel is a rendezvous, so with no receiver blocked in `recv`, even the first `try_send` reports `Full`.
- **Task 3.** Calling `producer.join().unwrap()` before the receiving loop deadlocks: the buffer holds 3 and 5, the producer blocks sending 2, and `join` waits for a producer that waits for a consumer, so the pad hangs until it times out.
- **Task 5.** Writing `let _ = send.send(7);` in a producer discards that error, so work vanishes silently when the consumer has gone. Example B's `.unwrap()` at least panics, naming `SendError`.
- **Task 6.** Switching to an unbounded `channel()` to avoid choosing removes backpressure: when the consumer is slower, the queue and its memory grow until the process fails.

## Self-check and next step

Why does the second immediate `try_send` in Example A return `Full(5)` instead of blocking, and what does the caller get back? What ends the receiving loop in Example B, and why would it wait forever if a sender clone were still alive? What should a consumer conclude when the channel disconnects before the expected number of messages?

Then work through [Self-check and review](../STUDY-GUIDE.md#self-check-and-review).

## Sources and execution boundary

Read [The Rust Book, 16.2 Message Passing](https://doc.rust-lang.org/book/ch16-02-message-passing.html) for how dropping every sender ends the receiver loop.

What the classroom does and does not prove: [Sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
