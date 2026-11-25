# swift-030: Cancellation and cleanup in asynchronous work

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-029`

## Learning objectives

Cancel asynchronous work cooperatively and clean up on every exit path. The central exercise is task 3: Write a bounded processing loop with cleanup on cancellation.

## Purpose and mental model

Task cancellation records a request that cooperative code can observe. It does not forcibly stop every instruction. A cancelled task can still return a value if it never checks cancellation. Distinguish a caller no longer wanting a result from the operation having stopped before effects occurred.

Use cancellation checks before admitting expensive work and at meaningful loop boundaries. Cleanup remains necessary on cancellation paths. Do not replay a state-changing request simply because an observer was cancelled; the first operation may have completed. The fixture observes cancellation deterministically without relying on a race between sleep durations.

## Vocabulary and concepts

**Cooperative cancellation:** Work responding to a request to stop.

**CancellationError:** The error signaling acknowledged task cancellation.

**Operation outcome:** The actual result or effect, distinct from observer interest.

## How to run this lesson

Example A's task loops until it observes cancellation, so if the `task.cancel()` line is removed the program never finishes; run that experiment only with a timeout in mind. Example B is deterministic because its body ignores cancellation. Task 4 is about a remote write whose result is unknown, so describe it in prose rather than code.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

Task.isCancelled inspects state and Task.checkCancellation throws CancellationError. A task handle can be cancelled and then awaited to observe its actual completion. Cancellation handlers require careful sendable state ownership.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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
        do {
          try Task.checkCancellation()
          return false
        } catch is CancellationError { return true } catch { return false }
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

**Trace.** `Task { ... }` starts unstructured work whose body loops while `Task.isCancelled` is false, yielding on each pass. The parent immediately calls `task.cancel()`, which sets the flag; it does not stop the task. Whenever the body next checks, the loop ends. `Task.checkCancellation()` then throws `CancellationError`, the matching catch returns true, and `await task.value` delivers that acknowledgment to the parent, whose check passes. Cancellation here is cooperative: the task decided how to respond.

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

**Trace.** This task's body returns 9 and never checks cancellation. The parent cancels it, perhaps before the body even starts, but the flag only matters to code that reads it. The body runs anyway and returns 9, and `await task.value` delivers 9. So the effect of a cancellation request on a given operation can be anything from immediate acknowledgment to no effect at all, depending on what the operation checks.

## Exercises

1. **Predict and explain.** Separate cancellation request from acknowledged completion.

2. **Guided modification.** Add a cancellation check before a simulated state-changing step.

3. **Independent construction.** Write a bounded processing loop with cleanup on cancellation.

4. **Diagnose a defect.** Diagnose retrying an unknown write merely because its waiter was cancelled.

5. **Boundary evidence.** Test cancellation before work and after an already completed result.

6. **Transfer and justify.** Design a receipt distinguishing success, confirmed cancellation and unknown outcome.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Polling cancellation in a tight CPU loop without yielding can waste resources. A cancellation handler must not race unsafely with the operation. Preserve result identity when deciding whether replay is safe.

Task 4's mistake is resending a payment because the caller stopped waiting. A cancelled waiter does not tell you whether the server applied the first write. The counterexample is a write that was applied and whose reply was lost: a blind retry applies it twice. A receipt with a stable operation identity, as in swift-032, makes the retry safe to check rather than repeat.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Cancel before observing a check) before changing anything, and confirm its observation: The task acknowledges cancellation and its completion is awaited.
2. Compare Example B (Cancellation need not prevent a result) with Example A and name the first line whose behavior differs. Its observation is: This task still returns 9 because its body does not check cancellation.
3. Before opening the explanation, check your task 3 attempt (Write a bounded processing loop with cleanup on cancellation) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain the difference between requesting cancellation and observing it. Name two ways a task body can notice cancellation. For task 5, predict the result when a task is cancelled after it has already returned a value. List the three states an operation receipt needs and why unknown must be one of them.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): Cooperative cancellation is explained in the book's Concurrency chapter; the standard library documents `Task.isCancelled`, `checkCancellation()` and `CancellationError`.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
