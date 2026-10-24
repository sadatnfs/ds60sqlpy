# csharp-031: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-031_solution.cs](csharp-031_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Reject immediate excess admission:** Bounded capacity is observable before work is lost or memory grows without limit. The first item is accepted and the second immediate write is refused.

**Drain after completion:** Closing admission does not discard buffered work. Completion becomes final after the reader drains it. Both admitted items are read after completion, and later writes fail.

## Reason through the six tasks

1. **Predict and explain.** Trace channel occupancy after each operation.

2. **Guided modification.** Increase capacity and predict which immediate writes succeed.

3. **Independent construction.** Build a bounded producer-consumer pipeline with explicit writer completion.

4. **Diagnose a defect.** Diagnose treating an empty open channel as permanently finished.

5. **Boundary evidence.** Test completion with zero buffered items and with a full buffer.

6. **Transfer and justify.** Choose wait, reject or drop behavior for a workload and explain what evidence the producer receives.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A channel connects producers and consumers through an asynchronous queue. Capacity is a resource policy: an unbounded queue can retain more work than memory or downstream systems can handle. A bounded channel makes overload visible through waiting, rejection or an explicit drop policy. Choose that policy from the value of the work, not from convenience.

Completion means no more writes will be admitted, while readers can still drain buffered items. A consumer should distinguish an empty-but-open channel from a completed channel. Cancellation and failure also need owners: somebody must complete the writer and account for admitted items. The single-process fixture teaches these states without depending on thread timing.

`Channel.CreateBounded<T>` creates a capacity-limited channel. TryWrite reports immediate admission. ReadAsync removes an item; Writer.Complete closes admission. Reader.Completion finishes after buffered work is drained.

An ignored false TryWrite result loses work. Blocking a producer while holding a lock needed by the consumer can deadlock. Completion and cancellation need a deliberate ownership policy.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
