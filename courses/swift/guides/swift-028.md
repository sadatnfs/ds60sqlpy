# swift-028: Async functions and suspension points

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-027`

## Learning objectives

Write an async adapter that returns a validated domain value. Then identify suspension points in an app load operation and explain what state may change around them.

## Purpose and mental model

An async function can suspend while waiting for another operation. Suspension is not the same as blocking a thread, and async does not automatically make CPU work parallel. Await marks a place where the current task may pause and other work may run. This boundary matters when shared state can change.

Keep ownership of the asynchronous result explicit. An unstructured task can outlive the scope that created it, while structured child tasks have a parent lifetime. This chapter uses tiny deterministic async functions, preparing for task groups and actors. A returned value proves this fixture completed, not that every future network or storage operation is reliable.

## Vocabulary and concepts

**Suspension point:** A place where a task may pause without holding a thread blocked.

**Task:** A unit of asynchronous work with an outcome and lifetime.

**Structured concurrency:** Child work whose lifetime is bounded by its parent scope.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`async` permits suspension; `await` acknowledges an async call. An async throwing method is called with try await. The entrypoint already supports async, so no semaphore or blocking bridge is needed.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

## Exercises

1. **Predict and explain.** Distinguish an async declaration from actual parallel execution.

2. **Guided modification.** Await two dependent calculations in order.

3. **Independent construction.** Write an async adapter that returns a validated domain value.

4. **Diagnose a defect.** Diagnose blocking with a semaphore to wait for async code on a constrained executor.

5. **Boundary evidence.** Test a valid and throwing async outcome.

6. **Transfer and justify.** Identify suspension points in an app load operation and explain what state may change around them.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Async does not promise a background thread. Do not block an executor waiting for work that needs the same executor. Retain and await meaningful results.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Suspension point, Task, Structured concurrency without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
