# rust-029: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-029_solution.rs](rust-029_solution.rs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Make full capacity observable:** The rejected value remains visible in the error instead of disappearing silently. One item is admitted and the next immediate send reports full capacity.

**Drain before declaring completion:** Producer lifetime and channel completion are explicitly connected. The receiver drains both values and ends after the sender is dropped.

## Task answers

### Task 1: Predict and explain

Trace queue occupancy and ownership after each send.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The rejected value remains visible in the error instead of disappearing silently. One item is admitted and the next immediate send reports full capacity.

### Task 2: Guided modification

Increase capacity and predict the accepted immediate sends.

No separate reference answer has been written for this task. Start from Example B: Producer lifetime and channel completion are explicitly connected. The receiver drains both values and ends after the sender is dropped.

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

### Task 4: Diagnose a defect

Diagnose a receiver waiting because an unused sender clone remains alive.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Joining a producer before draining a full bounded channel can deadlock. Ignoring a failed send loses work. Channel capacity does not bound work already started outside the channel.

### Task 5: Boundary evidence

Test no messages and a disconnected receiver.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Make full capacity observable) and Example B (Drain before declaring completion).

### Task 6: Transfer and justify

Choose blocking, rejection or intentional dropping for a workload and explain producer evidence.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Channel**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A channel transfers values between producers and consumers. Sending can move ownership so the receiving side becomes responsible for the value. A bounded synchronous channel limits how much work can wait in memory. Its capacity is an admission policy, not merely a performance tuning number.

A receiver can finish when all senders are dropped and buffered items are drained. Keeping an unused sender clone alive can therefore keep a consumer waiting. Join producers and observe send/receive errors deliberately. Avoid deadlock by ensuring a blocked producer has a consumer that can still run.

sync_channel creates bounded storage. try_send reports immediate full or disconnected states. send may block until capacity exists. Receiver iteration drains until sender ownership ends.

Joining a producer before draining a full bounded channel can deadlock. Ignoring a failed send loses work. Channel capacity does not bound work already started outside the channel.

## Review before continuing

Run the reference and confirm that it prints `rust-029: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
