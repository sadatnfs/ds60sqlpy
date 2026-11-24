# rust-029: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-029_solution.rs](rust-029_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Make full capacity observable:** The rejected value remains visible in the error instead of disappearing silently. One item is admitted and the next immediate send reports full capacity.

**Drain before declaring completion:** Producer lifetime and channel completion are explicitly connected. The receiver drains both values and ends after the sender is dropped.

## Task answers

### Task 1: Predict and explain

Trace queue occupancy and ownership after each send.

**Written answer.** Example A: `try_send(4)` puts 4 in the one-slot buffer (occupancy 1). `try_send(5)` returns `Err(TrySendError::Full(5))`, so 5 comes back to the caller and occupancy stays 1. `recv()` moves 4 to the receiver (occupancy 0). Example B: `move` gives `send` to the worker, which sends 2 and 3, and when its closure ends, `send` is dropped.

**Why it is correct.** A value is owned by the buffer between send and receive, and a refused value is returned inside the error. Once the last sender is dropped, the receiver still yields buffered items and only then ends.

**Plausible wrong approach.** Expecting `try_send(5)` to wait for space, or to discard 5, misreads the API: `try_send` never blocks, and `Full` hands the value back so the caller decides what to do with it.

**How to verify.** After Example A's `recv`, add `send.try_send(6)?;` and `assert_eq!(receive.try_recv()?, 6);`: the freed slot accepts one more item.

### Task 2: Guided modification

Increase capacity and predict the accepted immediate sends.

**Written answer.** With `sync_channel(2)`, `try_send(4)` and `try_send(5)` both succeed, and `try_send(6)` returns `Err(TrySendError::Full(6))`. `recv` then yields 4 and then 5.

**Why it is correct.** With no receiver waiting, a `sync_channel(n)` buffers exactly n unreceived items, so the number of accepted immediate sends equals the capacity.

**Plausible wrong approach.** Predicting capacity plus one, or that `sync_channel(0)` accepts a single item, is wrong: a zero-capacity channel is a rendezvous, so with no receiver blocked in `recv`, even the first `try_send` reports `Full`.

**How to verify.** Assert the two `Ok` sends, `matches!(send.try_send(6), Err(TrySendError::Full(6)))` and the 4 then 5 order. Then `let (zero, _keep) = sync_channel::<i32>(0);` and assert `zero.try_send(1)` is `Full(1)`; the `_keep` binding holds the receiver alive.

### Task 3: Independent construction

Build a bounded producer-consumer report pipeline.

**Reference answer.** The same statements run as the `Task 3` block of the reference program; here they are wrapped in `main` as a complete file.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let (send, receive) = std::sync::mpsc::sync_channel::<u32>(2);
    let producer = std::thread::spawn(move || {
        for quantity in [3, 5, 2] {
            send.send(quantity).unwrap();
        }
    });
    let mut report = Vec::new();
    for quantity in receive {
        report.push(format!("qty={quantity}"));
    }
    producer.join().unwrap();
    assert_eq!(report, ["qty=3", "qty=5", "qty=2"]);
    Ok(())
}
```

**Observe:** The consumer reports qty=3, qty=5 and qty=2 in order and then stops.

sync_channel(2) blocks the producer when two items are waiting, and the receiving loop ends when the producer's sender is dropped.

**Plausible wrong approach.** Calling `producer.join().unwrap()` before the receiving loop deadlocks: the buffer holds 3 and 5, the producer blocks sending 2, and `join` waits for a producer that waits for a consumer, so the pad hangs until it times out.

**How to verify.** Run the block and confirm the report order. Extend the input to `[3, 5, 2, 7]` with `qty=7` appended to the expected report: the bounded buffer still drains and the loop ends.

### Task 4: Diagnose a defect

Diagnose a receiver waiting because an unused sender clone remains alive.

**Written answer.** The defect: `let extra = send.clone();` in `main` before Example B's worker takes `send`. The worker sends 2 and 3 and drops its sender, but `extra` keeps the channel connected, so `receive.iter().sum()` waits forever after the two values. Fix it with `drop(extra);` before draining, or do not create the clone.

**Why it is correct.** The receiver ends only when every sender is gone. A clone that never sends still counts as a live producer.

**Plausible wrong approach.** Adding `worker.join()` before the sum does not help: the worker finishes (both values fit in the buffer), but joining it does not drop `extra`, so the iterator still waits.

**How to verify.** Use `receive.recv_timeout(std::time::Duration::from_millis(100))` after taking 2 and 3: it returns `Err(RecvTimeoutError::Timeout)` while `extra` is alive and `Err(RecvTimeoutError::Disconnected)` after `drop(extra)`.

### Task 5: Boundary evidence

Test no messages and a disconnected receiver.

**Written answer.** No messages: `let (send, receive) = sync_channel::<i32>(1); drop(send);` then `receive.iter().count() == 0` and `receive.recv().is_err()`. Disconnected receiver: create another pair, `drop(receive);` and `send.send(7)` returns `Err(SendError(7))`.

**Why it is correct.** With no senders and an empty buffer, the receiver reports completion at once. With no receiver, nobody can ever take the value, so `send` fails and returns 7 inside the error instead of losing it.

**Plausible wrong approach.** Writing `let _ = send.send(7);` in a producer discards that error, so work vanishes silently when the consumer has gone. Example B's `.unwrap()` at least panics, naming `SendError`.

**How to verify.** Assert `send.send(7).unwrap_err().0 == 7` for the disconnected case, and the zero count for the empty case; the marker follows.

### Task 6: Transfer and justify

Choose blocking, rejection or intentional dropping for a workload and explain producer evidence.

**Written answer.** For an inventory import where every row matters, use blocking `send` on a `sync_channel`, so a slow writer slows the reader. For a request path that must answer quickly, use `try_send` and reject on `Full`, returning a retry signal. For telemetry samples, drop deliberately and count the drops. In each case the producer records sent, rejected and dropped counts.

**Why it is correct.** Each policy states who absorbs overload: the producer waits, the caller retries, or the data is knowingly lost. The counts are the producer's evidence of which happened. A limitation is that capacity does not bound work already started outside the channel.

**Plausible wrong approach.** Switching to an unbounded `channel()` to avoid choosing removes backpressure: when the consumer is slower, the queue and its memory grow until the process fails.

**How to verify.** With `sync_channel(1)` and no consumer running, `try_send` each of `[1, 2, 3]`, collecting values from `Err(TrySendError::Full(value))`. Assert the rejected list is `vec![2, 3]` and `receive.recv()?` is 1.

## Mechanism and diagnostic reasoning

A channel transfers values between producers and consumers. Sending can move ownership so the receiving side becomes responsible for the value. A bounded synchronous channel limits how much work can wait in memory. Its capacity is an admission policy, not merely a performance tuning number.

A receiver can finish when all senders are dropped and buffered items are drained. Keeping an unused sender clone alive can therefore keep a consumer waiting. Join producers and observe send/receive errors deliberately. Avoid deadlock by ensuring a blocked producer has a consumer that can still run.

sync_channel creates bounded storage. try_send reports immediate full or disconnected states. send may block until capacity exists. Receiver iteration drains until sender ownership ends.

Joining a producer before draining a full bounded channel can deadlock. Ignoring a failed send loses work. Channel capacity does not bound work already started outside the channel.

## Review before continuing

Run the reference and confirm that it prints `rust-029: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
