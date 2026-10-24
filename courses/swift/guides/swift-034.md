# swift-034: AsyncSequence, streams and bounded buffering

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-033`

## Learning objectives

Build a finite event stream with explicit completion ownership. Then choose lossless backpressure or deliberate dropping for a real event source and explain cleanup on cancellation.

## Purpose and mental model

AsyncSequence delivers values over time through asynchronous iteration. It can model events, streamed records or incremental results. A consumer awaits each next value instead of requiring the entire sequence immediately. The producer and consumer still need a clear completion and cancellation relationship.

AsyncStream bridges callback-style production into this model. Its buffering policy matters: an unbounded default can retain excessive events when a consumer is slow. A bounded policy can drop values, so the producer must inspect yield results when loss matters. The fixture produces a finite sequence synchronously and then finishes, making the data contract deterministic.

## Vocabulary and concepts

**AsyncSequence:** A sequence whose next value can require asynchronous waiting.

**Buffer policy:** A rule for retaining or dropping values awaiting consumption.

**Termination:** The event ending production and releasing owned resources.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

AsyncStream constructs a stream and exposes a continuation. yield admits an element according to the buffer policy; finish ends production. for await consumes until completion.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Consume a finite stream

Explicit finish prevents the consumer from waiting forever after the last value.

```swift
import Foundation



@main
struct LessonMain {
    static func main() async throws {
        do {
            let stream = AsyncStream<Int> { continuation in continuation.yield(2); continuation.yield(3); continuation.finish() }
            var total = 0
            for await value in stream { total += value }
            precondition(total == 5)
        }
        print("swift-034: passed")
    }
}
```

**Observe:** The finite stream totals 5 and terminates.

### Example B: Make drop behavior observable

Because production finishes before consumption starts here, the buffer outcome is deterministic.

```swift
import Foundation



@main
struct LessonMain {
    static func main() async throws {
        do {
            let stream = AsyncStream<Int>(bufferingPolicy: .bufferingNewest(1)) { continuation in continuation.yield(1); continuation.yield(2); continuation.finish() }
            var values: [Int] = []
            for await value in stream { values.append(value) }
            precondition(values == [2])
        }
        print("swift-034: passed")
    }
}
```

**Observe:** The newest-one policy retains 2 and drops the older buffered value.

## Exercises

1. **Predict and explain.** Trace production, buffering and completion.

2. **Guided modification.** Use bufferingOldest(1) and predict the retained value.

3. **Independent construction.** Build a finite event stream with explicit completion ownership.

4. **Diagnose a defect.** Diagnose an infinite wait caused by never finishing a finite producer.

5. **Boundary evidence.** Test zero events and a buffer overflow policy.

6. **Transfer and justify.** Choose lossless backpressure or deliberate dropping for a real event source and explain cleanup on cancellation.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

AsyncStream buffering is not automatically backpressure. Ignoring dropped values can silently lose work. A continuation retained forever can keep resources alive after consumers stop.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain AsyncSequence, Buffer policy, Termination without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
