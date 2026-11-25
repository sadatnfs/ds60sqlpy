# swift-034: AsyncSequence, streams and bounded buffering

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-033`

## Learning objectives

Produce and consume AsyncStreams with explicit completion and bounded buffering. The central exercise is task 3: Build a finite event stream with explicit completion ownership.

## Purpose and mental model

AsyncSequence delivers values over time through asynchronous iteration. It can model events, streamed records or incremental results. A consumer awaits each next value instead of requiring the entire sequence immediately. The producer and consumer still need a clear completion and cancellation relationship.

AsyncStream bridges callback-style production into this model. Its buffering policy matters: an unbounded default can retain excessive events when a consumer is slow. A bounded policy can drop values, so the producer must inspect yield results when loss matters. The fixture produces a finite sequence synchronously and then finishes, making the data contract deterministic.

## Vocabulary and concepts

**AsyncSequence:** A sequence whose next value can require asynchronous waiting.

**Buffer policy:** A rule for retaining or dropping values awaiting consumption.

**Termination:** The event ending production and releasing owned resources.

## How to run this lesson

Both streams finish before consumption starts, so their output is deterministic. Remove `continuation.finish()` from Example A and the `for await` loop waits forever after the last value, so the marker never prints; that is task 4's defect, and you will need to stop the run yourself. Task 2 swaps the buffering policy.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

AsyncStream constructs a stream and exposes a continuation. yield admits an element according to the buffer policy; finish ends production. for await consumes until completion.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Consume a finite stream

Explicit finish prevents the consumer from waiting forever after the last value.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let stream = AsyncStream<Int> { continuation in
        continuation.yield(2)
        continuation.yield(3)
        continuation.finish()
      }
      var total = 0
      for await value in stream { total += value }
      precondition(total == 5)
    }
    print("swift-034: passed")
  }
}
```

**Observe:** The finite stream totals 5 and terminates.

**Trace.** The `AsyncStream` initializer runs its closure immediately with a continuation. The closure yields 2 and 3 into the stream's buffer and then calls `finish()`, which marks the end. The consumer's `for await` loop receives 2, adding it to give 2, then 3, giving 5, and then sees the finish and exits. Without the finish, the loop would keep waiting for a value that never arrives, because the stream cannot tell a slow producer from a completed one.

### Example B: Make drop behavior observable

Because production finishes before consumption starts here, the buffer outcome is deterministic.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let stream = AsyncStream<Int>(bufferingPolicy: .bufferingNewest(1)) { continuation in
        continuation.yield(1)
        continuation.yield(2)
        continuation.finish()
      }
      var values: [Int] = []
      for await value in stream { values.append(value) }
      precondition(values == [2])
    }
    print("swift-034: passed")
  }
}
```

**Observe:** The newest-one policy retains 2 and drops the older buffered value.

**Trace.** The policy `.bufferingNewest(1)` keeps at most one unconsumed value and discards the older one when a newer value arrives. Yielding 1 fills the buffer. Yielding 2 finds it full, drops 1 and stores 2. `finish()` ends the stream. The consumer then reads only 2, and the check compares against `[2]`. With `.bufferingOldest(1)`, the buffer would keep 1 and reject 2, so the result would be `[1]`.

## Exercises

1. **Predict and explain.** Trace production, buffering and completion.

2. **Guided modification.** Use bufferingOldest(1) and predict the retained value.

3. **Independent construction.** Build a finite event stream with explicit completion ownership.

4. **Diagnose a defect.** Diagnose an infinite wait caused by never finishing a finite producer.

5. **Boundary evidence.** Test zero events and a buffer overflow policy.

6. **Transfer and justify.** Choose lossless backpressure or deliberate dropping for a real event source and explain cleanup on cancellation.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

AsyncStream buffering is not automatically backpressure. Ignoring dropped values can silently lose work. A continuation retained forever can keep resources alive after consumers stop.

A buffering-policy bug only shows when production outruns consumption. The counterexample for task 5 yields three values into a one-slot buffer before consuming: newest keeps the last, oldest keeps the first, and unbounded keeps all three. Zero events with an immediate finish must produce an empty array and end the loop at once.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Consume a finite stream) before changing anything, and confirm its observation: The finite stream totals 5 and terminates.
2. Compare Example B (Make drop behavior observable) with Example A and name the first line whose behavior differs. Its observation is: The newest-one policy retains 2 and drops the older buffered value.
3. Before opening the explanation, check your task 3 attempt (Build a finite event stream with explicit completion ownership) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain who owns the continuation and who must call `finish()`. Say what the default buffering policy is and when it can grow without bound. Choose dropping or lossless delivery for sensor readings and for payment events, and explain what the consumer loses in each case.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The standard library reference documents `AsyncStream`, its `Continuation` and buffering policies; the Swift book's Concurrency chapter covers asynchronous sequences.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-034: AsyncSequence, streams and bounded buffering.
Read courses/swift/guides/swift-034.md and courses/swift/lessons/swift-034.swift. Prerequisites: swift-033.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-034_solution.swift and
courses/swift/solutions/swift-034_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
