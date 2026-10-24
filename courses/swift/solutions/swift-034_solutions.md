# swift-034: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-034_solution.swift](swift-034_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Consume a finite stream:** Explicit finish prevents the consumer from waiting forever after the last value. The finite stream totals 5 and terminates.

**Make drop behavior observable:** Because production finishes before consumption starts here, the buffer outcome is deterministic. The newest-one policy retains 2 and drops the older buffered value.

## Reason through the six tasks

1. **Predict and explain.** Trace production, buffering and completion.

2. **Guided modification.** Use bufferingOldest(1) and predict the retained value.

3. **Independent construction.** Build a finite event stream with explicit completion ownership.

4. **Diagnose a defect.** Diagnose an infinite wait caused by never finishing a finite producer.

5. **Boundary evidence.** Test zero events and a buffer overflow policy.

6. **Transfer and justify.** Choose lossless backpressure or deliberate dropping for a real event source and explain cleanup on cancellation.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

AsyncSequence delivers values over time through asynchronous iteration. It can model events, streamed records or incremental results. A consumer awaits each next value instead of requiring the entire sequence immediately. The producer and consumer still need a clear completion and cancellation relationship.

AsyncStream bridges callback-style production into this model. Its buffering policy matters: an unbounded default can retain excessive events when a consumer is slow. A bounded policy can drop values, so the producer must inspect yield results when loss matters. The fixture produces a finite sequence synchronously and then finishes, making the data contract deterministic.

AsyncStream constructs a stream and exposes a continuation. yield admits an element according to the buffer policy; finish ends production. for await consumes until completion.

AsyncStream buffering is not automatically backpressure. Ignoring dropped values can silently lose work. A continuation retained forever can keep resources alive after consumers stop.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
