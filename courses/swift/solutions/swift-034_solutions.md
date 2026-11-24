# swift-034: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-034_solution.swift](swift-034_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Consume a finite stream:** Explicit finish prevents the consumer from waiting forever after the last value. The finite stream totals 5 and terminates.

**Make drop behavior observable:** Because production finishes before consumption starts here, the buffer outcome is deterministic. The newest-one policy retains 2 and drops the older buffered value.

## Task answers

### Task 1: Predict and explain

Trace production, buffering and completion.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let (stream, continuation) = AsyncStream<Int>.makeStream(bufferingPolicy: .bufferingNewest(5))
var buffered = -1
if case .enqueued(let remaining) = continuation.yield(2) { buffered = remaining }
precondition(buffered == 4)
continuation.finish()
var terminated = false
if case .terminated = continuation.yield(9) { terminated = true }
precondition(terminated)
var values: [Int] = []
for await value in stream { values.append(value) }
precondition(values == [2])
```

**Observe:** Yielding 2 reports 4 free buffer slots, a yield after finish reports terminated, and the consumer receives only [2].

The producer yields into the buffer before anyone reads, finish marks completion, and later yields are refused; the consumer drains the buffer and its loop ends at the finish.

### Task 2: Guided modification

Use bufferingOldest(1) and predict the retained value.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
let stream = AsyncStream<Int>(bufferingPolicy: .bufferingOldest(1)) { continuation in
  continuation.yield(1)
  continuation.yield(2)
  continuation.finish()
}
var values: [Int] = []
for await value in stream { values.append(value) }
precondition(values == [1])
```

**Observe:** With bufferingOldest(1), the stream keeps 1 and drops 2.

The oldest policy keeps what is already buffered and discards new arrivals when full, the opposite of bufferingNewest, which kept 2.

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

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
let (stream, continuation) = AsyncStream<Int>.makeStream()
continuation.yield(1)
continuation.yield(2)
continuation.finish()
var count = 0
for await _ in stream { count += 1 }
precondition(count == 2)
```

**Observe:** After two values and finish, the loop counts 2 and ends.

for await only ends when the stream finishes; without continuation.finish() the consumer would wait forever after 2, so the owner of a finite producer must finish it on every path.

### Task 5: Boundary evidence

Test zero events and a buffer overflow policy.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
let (empty, emptyContinuation) = AsyncStream<Int>.makeStream()
emptyContinuation.finish()
var none: [Int] = []
for await value in empty { none.append(value) }
precondition(none.isEmpty)
let (stream, continuation) = AsyncStream<Int>.makeStream(bufferingPolicy: .bufferingOldest(2))
continuation.yield(1)
continuation.yield(2)
var dropped: Int?
if case .dropped(let value) = continuation.yield(3) { dropped = value }
continuation.finish()
var kept: [Int] = []
for await value in stream { kept.append(value) }
precondition(dropped == 3 && kept == [1, 2])
```

**Observe:** A stream finished with no events yields nothing; with room for two, the third yield reports dropped 3 and the consumer gets [1, 2].

The yield result makes the overflow policy observable at the producer, so dropped work can be counted or logged rather than vanishing silently.

### Task 6: Transfer and justify

Choose lossless backpressure or deliberate dropping for a real event source and explain cleanup on cancellation.

No single reference answer exists: several designs can satisfy this transfer task. Build yours from the task 3 answer above (Build a finite event stream with explicit completion ownership) and the mechanism described below, and state one limitation of your choice.

## Solution reasoning

**Approach.** Example A builds an `AsyncStream` that yields 2 and 3 and then calls `finish()`, and a `for await` loop sums them. Example B uses `.bufferingNewest(1)` and yields 1 and 2 before finishing, then consumes. The task 3 answer builds a finite event stream whose producer owns completion.

**Why it is correct.** Because `finish()` is called, the consumer's loop ends after 2 and 3, so the total is 5. In Example B both yields happen inside the build closure before consumption starts; a newest-one buffer keeps only the last element, so 1 is dropped and the loop sees `[2]`. In task 3 the consumer receives start, progress and done, and its loop ends.

**A plausible wrong approach.** Omitting `continuation.finish()` is the task 4 defect: the `for await` loop never ends, so the program waits forever after the last value and never prints the marker. Assuming a buffer applies backpressure is another error; Example B shows it drops values instead of slowing the producer.

**How to verify.** For task 2, switch to `.bufferingOldest(1)` and predict `[1]`, since the first buffered value is kept and 2 is dropped. For task 5, a stream that finishes without yielding gives a total of 0.

## Mechanism and diagnostic reasoning

AsyncSequence delivers values over time through asynchronous iteration. It can model events, streamed records or incremental results. A consumer awaits each next value instead of requiring the entire sequence immediately. The producer and consumer still need a clear completion and cancellation relationship.

AsyncStream bridges callback-style production into this model. Its buffering policy matters: an unbounded default can retain excessive events when a consumer is slow. A bounded policy can drop values, so the producer must inspect yield results when loss matters. The fixture produces a finite sequence synchronously and then finishes, making the data contract deterministic.

AsyncStream constructs a stream and exposes a continuation. yield admits an element according to the buffer policy; finish ends production. for await consumes until completion.

AsyncStream buffering is not automatically backpressure. Ignoring dropped values can silently lose work. A continuation retained forever can keep resources alive after consumers stop.

## Review before continuing

Run the reference and confirm that it prints `swift-034: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
