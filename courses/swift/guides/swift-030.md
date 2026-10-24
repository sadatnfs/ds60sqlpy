# swift-030: Cancellation and cleanup in asynchronous work

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-029`

## Learning objectives

Write a bounded processing loop with cleanup on cancellation. Then design a receipt distinguishing success, confirmed cancellation and unknown outcome.

## Purpose and mental model

Task cancellation records a request that cooperative code can observe. It does not forcibly stop every instruction. A cancelled task can still return a value if it never checks cancellation. Distinguish a caller no longer wanting a result from the operation having stopped before effects occurred.

Use cancellation checks before admitting expensive work and at meaningful loop boundaries. Cleanup remains necessary on cancellation paths. Do not replay a state-changing request simply because an observer was cancelled; the first operation may have completed. The fixture observes cancellation deterministically without relying on a race between sleep durations.

## Vocabulary and concepts

**Cooperative cancellation:** Work responding to a request to stop.

**CancellationError:** The error signaling acknowledged task cancellation.

**Operation outcome:** The actual result or effect, distinct from observer interest.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

Task.isCancelled inspects state and Task.checkCancellation throws CancellationError. A task handle can be cancelled and then awaited to observe its actual completion. Cancellation handlers require careful sendable state ownership.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Cancel before observing a check

The loop observes cancellation state rather than guessing a scheduling delay.

```swift
import Foundation



@main
struct LessonMain {
    static func main() async throws {
        do {
            let task = Task {
                while !Task.isCancelled { await Task.yield() }
                do { try Task.checkCancellation(); return false } catch is CancellationError { return true } catch { return false }
            }
            task.cancel()
            let acknowledged = await task.value
            precondition(acknowledged)
        }
        print("swift-030: passed")
    }
}
```

**Observe:** The task acknowledges cancellation and its completion is awaited.

### Example B: Cancellation need not prevent a result

A cancellation request alone is not proof that an operation failed to execute.

```swift
import Foundation



@main
struct LessonMain {
    static func main() async throws {
        do {
            let task = Task { 9 }
            task.cancel()
            let value = await task.value
            precondition(value == 9)
        }
        print("swift-030: passed")
    }
}
```

**Observe:** This task still returns 9 because its body does not check cancellation.

## Exercises

1. **Predict and explain.** Separate cancellation request from acknowledged completion.

2. **Guided modification.** Add a cancellation check before a simulated state-changing step.

3. **Independent construction.** Write a bounded processing loop with cleanup on cancellation.

4. **Diagnose a defect.** Diagnose retrying an unknown write merely because its waiter was cancelled.

5. **Boundary evidence.** Test cancellation before work and after an already completed result.

6. **Transfer and justify.** Design a receipt distinguishing success, confirmed cancellation and unknown outcome.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Polling cancellation in a tight CPU loop without yielding can waste resources. A cancellation handler must not race unsafely with the operation. Preserve result identity when deciding whether replay is safe.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Cooperative cancellation, CancellationError, Operation outcome without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-030: Cancellation and cleanup in asynchronous work.
Read courses/swift/guides/swift-030.md and courses/swift/lessons/swift-030.swift. Prerequisites: swift-029.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-030_solution.swift and
courses/swift/solutions/swift-030_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
