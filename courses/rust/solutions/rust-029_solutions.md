# rust-029: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-029_solution.rs](rust-029_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Make full capacity observable:** The rejected value remains visible in the error instead of disappearing silently. One item is admitted and the next immediate send reports full capacity.

**Drain before declaring completion:** Producer lifetime and channel completion are explicitly connected. The receiver drains both values and ends after the sender is dropped.

## Reason through the six tasks

1. **Predict and explain.** Trace queue occupancy and ownership after each send.

2. **Guided modification.** Increase capacity and predict the accepted immediate sends.

3. **Independent construction.** Build a bounded producer-consumer report pipeline.

4. **Diagnose a defect.** Diagnose a receiver waiting because an unused sender clone remains alive.

5. **Boundary evidence.** Test no messages and a disconnected receiver.

6. **Transfer and justify.** Choose blocking, rejection or intentional dropping for a workload and explain producer evidence.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A channel transfers values between producers and consumers. Sending can move ownership so the receiving side becomes responsible for the value. A bounded synchronous channel limits how much work can wait in memory. Its capacity is an admission policy, not merely a performance tuning number.

A receiver can finish when all senders are dropped and buffered items are drained. Keeping an unused sender clone alive can therefore keep a consumer waiting. Join producers and observe send/receive errors deliberately. Avoid deadlock by ensuring a blocked producer has a consumer that can still run.

sync_channel creates bounded storage. try_send reports immediate full or disconnected states. send may block until capacity exists. Receiver iteration drains until sender ownership ends.

Joining a producer before draining a full bounded channel can deadlock. Ignoring a failed send loses work. Channel capacity does not bound work already started outside the channel.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
