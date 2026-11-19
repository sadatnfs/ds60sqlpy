# swift-034: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-034_solution.swift](swift-034_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Consume a finite stream:** Explicit finish prevents the consumer from waiting forever after the last value. The finite stream totals 5 and terminates.

**Make drop behavior observable:** Because production finishes before consumption starts here, the buffer outcome is deterministic. The newest-one policy retains 2 and drops the older buffered value.

## Task answers

### Task 1: Predict and explain

Trace production, buffering and completion.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Explicit finish prevents the consumer from waiting forever after the last value. The finite stream totals 5 and terminates.

### Task 2: Guided modification

Use bufferingOldest(1) and predict the retained value.

No separate reference answer has been written for this task. Start from Example B: Because production finishes before consumption starts here, the buffer outcome is deterministic. The newest-one policy retains 2 and drops the older buffered value.

### Task 3: Independent construction

Build a finite event stream with explicit completion ownership.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
let (events, continuation) = AsyncStream<String>.makeStream()
let producer = Task {
  for name in ["start", "progress", "done"] { continuation.yield(name) }
  continuation.finish()
}
var received: [String] = []
for await event in events { received.append(event) }
await producer.value
precondition(received == ["start", "progress", "done"])
```

**Observe:** The consumer receives start, progress and done, and its loop ends.

The producer owns the continuation and calls finish(); without it the consumer's for await would wait forever.

### Task 4: Diagnose a defect

Diagnose an infinite wait caused by never finishing a finite producer.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: AsyncStream buffering is not automatically backpressure. Ignoring dropped values can silently lose work. A continuation retained forever can keep resources alive after consumers stop.

### Task 5: Boundary evidence

Test zero events and a buffer overflow policy.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Consume a finite stream) and Example B (Make drop behavior observable).

### Task 6: Transfer and justify

Choose lossless backpressure or deliberate dropping for a real event source and explain cleanup on cancellation.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **AsyncSequence**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

AsyncSequence delivers values over time through asynchronous iteration. It can model events, streamed records or incremental results. A consumer awaits each next value instead of requiring the entire sequence immediately. The producer and consumer still need a clear completion and cancellation relationship.

AsyncStream bridges callback-style production into this model. Its buffering policy matters: an unbounded default can retain excessive events when a consumer is slow. A bounded policy can drop values, so the producer must inspect yield results when loss matters. The fixture produces a finite sequence synchronously and then finishes, making the data contract deterministic.

AsyncStream constructs a stream and exposes a continuation. yield admits an element according to the buffer policy; finish ends production. for await consumes until completion.

AsyncStream buffering is not automatically backpressure. Ignoring dropped values can silently lose work. A continuation retained forever can keep resources alive after consumers stop.

## Review before continuing

Run the reference and confirm that it prints `swift-034: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
