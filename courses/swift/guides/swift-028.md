# swift-028: Async functions and suspension points

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-027`

## Learning objectives

Write async functions and explain where suspension points occur. The central exercise is task 3: Write an async adapter that returns a validated domain value.

## Purpose and mental model

An async function can suspend while waiting for another operation. Suspension is not the same as blocking a thread, and async does not automatically make CPU work parallel. Await marks a place where the current task may pause and other work may run. This boundary matters when shared state can change.

Keep ownership of the asynchronous result explicit. An unstructured task can outlive the scope that created it, while structured child tasks have a parent lifetime. This chapter uses tiny deterministic async functions, preparing for task groups and actors. A returned value proves this fixture completed, not that every future network or storage operation is reliable.

## Vocabulary and concepts

**Suspension point:** A place where a task may pause without holding a thread blocked.

**Task:** A unit of asynchronous work with an outcome and lifetime.

**Structured concurrency:** Child work whose lifetime is bounded by its parent scope.

## How to run this lesson

`main` is already `async throws`, so you can `await` directly in it. Calling an async function without `await` fails to compile with a message that the expression is async but not marked with `await`. Task 4 is a written diagnosis; do not run a semaphore wait in the pad, because blocking the only executor thread can hang the program.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`async` permits suspension; `await` acknowledges an async call. An async throwing method is called with try await. The entrypoint already supports async, so no semaphore or blocking bridge is needed.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Await an asynchronous result

The fixture introduces the call boundary without pretending a tiny calculation needs a separate thread.

```swift
import Foundation

enum AsyncError: Error { case invalid }

@main
struct LessonMain {
  static func main() async throws {
    do {
      func double(_ value: Int) async -> Int { value * 2 }
      let result = await double(4)
      precondition(result == 8)
    }
    print("swift-028: passed")
  }
}
```

**Observe:** The awaited result is 8.

**Trace.** `double` is declared `async`, which means it may suspend, not that it runs on another thread. The call `await double(4)` marks the point where the caller could suspend. Here the body never actually suspends: it multiplies 4 by 2 and returns 8 at once. The check confirms 8. Marking a tiny calculation as async only shows the syntax of the call boundary; it does not make the work faster or parallel.

### Example B: Propagate async failure

Suspension capability does not change the requirement to handle failure honestly.

```swift
import Foundation

enum AsyncError: Error { case invalid }

@main
struct LessonMain {
  static func main() async throws {
    do {
      func validated(_ value: Int) async throws -> Int {
        guard value >= 0 else { throw AsyncError.invalid }
        return value
      }
      let accepted = try await validated(3)
      precondition(accepted == 3)
      var rejected = false
      do { _ = try await validated(-1) } catch AsyncError.invalid { rejected = true }
      precondition(rejected)
    }
    print("swift-028: passed")
  }
}
```

**Observe:** The async boundary preserves both the valid result and the domain error.

**Trace.** `validated` is both `async` and `throws`, so callers write `try await`, with `try` before `await`. For 3 the guard passes and 3 is returned. For -1 the guard fails and the function throws `AsyncError.invalid`. The do-catch receives the error exactly as it would from a synchronous throwing function, and sets `rejected`. Suspension and failure are independent features: an async function can fail, succeed or never suspend at all.

## Exercises

1. **Predict and explain.** Distinguish an async declaration from actual parallel execution.

2. **Guided modification.** Await two dependent calculations in order.

3. **Independent construction.** Write an async adapter that returns a validated domain value.

4. **Diagnose a defect.** Diagnose blocking with a semaphore to wait for async code on a constrained executor.

5. **Boundary evidence.** Test a valid and throwing async outcome.

6. **Transfer and justify.** Identify suspension points in an app load operation and explain what state may change around them.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Async does not promise a background thread. Do not block an executor waiting for work that needs the same executor. Retain and await meaningful results.

For task 2, the order of two dependent awaits matters only if the second uses the first's result. Await the double of 4, then the double of that result: you must get 16. A version that starts both from the original 4 gets 8 twice. For task 5, keep both the accepted 3 and the rejected -1, since checking only the success path misses a missing guard.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Await an asynchronous result) before changing anything, and confirm its observation: The awaited result is 8.
2. Compare Example B (Propagate async failure) with Example A and name the first line whose behavior differs. Its observation is: The async boundary preserves both the valid result and the domain error.
3. Before opening the explanation, check your task 3 attempt (Write an async adapter that returns a validated domain value) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain the difference between an async function and parallel execution in one sentence each. State the correct order of `try` and `await` on a throwing async call. Name two things that could change in an app's state between the line before an `await` and the line after it.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The Concurrency chapter of the Swift book covers defining and calling asynchronous functions, suspension points and asynchronous error handling.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-028: Async functions and suspension points.
Read courses/swift/guides/swift-028.md and courses/swift/lessons/swift-028.swift. Prerequisites: swift-027.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-028_solution.swift and
courses/swift/solutions/swift-028_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
