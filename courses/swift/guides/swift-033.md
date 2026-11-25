# swift-033: Sendable and strict concurrency boundaries

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-032`

## Learning objectives

Pass only Sendable values across concurrency boundaries under Swift 6 strict checking. The central exercise is task 3: Replace a shared mutable result class with a sendable value result.

## Purpose and mental model

Sendable describes values that can cross concurrency boundaries without introducing unsafe shared mutation. Immutable structs composed of sendable members are a natural fit. A mutable reference type requires a real synchronization or isolation story; adding unchecked Sendable only removes the compiler's protection and transfers responsibility to the programmer.

Swift 6 checking makes many previously implicit assumptions visible. Treat diagnostics as design feedback: identify the owner of each mutable value and the boundary across which it moves. A MainActor-isolated UI model and a background actor can exchange immutable snapshots instead of sharing writable object graphs. This is both a language rule and an architecture technique.

## Vocabulary and concepts

**Sendable:** A capability for safely crossing concurrency boundaries.

**Isolation domain:** The context owning access to mutable state.

**Snapshot:** An independent value representing state at one point.

## How to run this lesson

`Snapshot` is declared `Sendable` above `LessonMain` in both examples. Under Swift 6 checking, a non-Sendable value captured by a `Task` closure produces a compile error, so the type annotation is doing real work. For task 4, compile a class marked `@unchecked Sendable` and note that the compiler accepts it without verifying anything.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`struct Snapshot: Sendable` declares a crossing contract. Actor calls and child tasks create concurrency boundaries. Capture immutable values and return results instead of mutating shared containers from several tasks.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Send an immutable snapshot

No mutable object identity is shared across the boundary.

```swift
import Foundation

struct Snapshot: Sendable {
  let name: String
  let quantity: Int
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let snapshot = Snapshot(name: "pear", quantity: 3)
      let task = Task { snapshot.quantity * 2 }
      let result = await task.value
      precondition(result == 6)
    }
    print("swift-033: passed")
  }
}
```

**Observe:** The task receives immutable value data and returns 6.

**Trace.** `snapshot` is a struct with two `let` properties, so it can never change after creation. The `Task` closure captures a copy of it, and because `Snapshot` is `Sendable` the compiler allows the capture to cross into concurrently executing code. The task reads quantity 3, returns 6, and `await task.value` delivers 6 to the parent. No mutable memory is shared between the two contexts, which is why no lock is needed.

### Example B: Return values to the owner

Child tasks produce values instead of concurrently mutating one array.

```swift
import Foundation

struct Snapshot: Sendable {
  let name: String
  let quantity: Int
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let result = await withTaskGroup(of: Snapshot.self, returning: [Snapshot].self) { group in
        group.addTask { Snapshot(name: "b", quantity: 2) }
        group.addTask { Snapshot(name: "a", quantity: 1) }
        var snapshots: [Snapshot] = []
        for await value in group { snapshots.append(value) }
        return snapshots.sorted { $0.name < $1.name }
      }
      precondition(result.map(\.name) == ["a", "b"])
    }
    print("swift-033: passed")
  }
}
```

**Observe:** The parent owns result aggregation and sorts it deterministically.

**Trace.** The group adds two children, one returning snapshot b with quantity 2 and one returning a with quantity 1. The parent collects whatever order they finish in into its own local array, then sorts by name with a closure comparing `$0.name < $1.name`. Mapping with the key path `\.name` extracts a then b. The children only return values; aggregation and ordering belong to the parent alone.

## Exercises

1. **Predict and explain.** Identify the owner of every value crossing a task boundary.

2. **Guided modification.** Add another immutable field to the snapshot.

3. **Independent construction.** Replace a shared mutable result class with a sendable value result.

4. **Diagnose a defect.** Diagnose an unchecked Sendable annotation hiding unsynchronized mutable state.

5. **Boundary evidence.** Test empty snapshots and multiple concurrent producers.

6. **Transfer and justify.** Design data exchange between a UI model and a background actor using immutable snapshots.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Sendable does not mean every operation is cheap or atomic. Unchecked conformance requires a justified invariant and tests. MainActor protects UI isolation but does not make long CPU work appropriate on that actor.

Task 4's annotation silences the checker: a class with a mutable array marked `@unchecked Sendable` compiles, and two tasks appending to it can corrupt the array or lose elements at runtime. The counterexample is many concurrent appends followed by a count check that sometimes fails. Replacing the class with a Sendable value returned to the parent removes the shared mutation entirely.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Send an immutable snapshot) before changing anything, and confirm its observation: The task receives immutable value data and returns 6.
2. Compare Example B (Return values to the owner) with Example A and name the first line whose behavior differs. Its observation is: The parent owns result aggregation and sorts it deterministically.
3. Before opening the explanation, check your task 3 attempt (Replace a shared mutable result class with a sendable value result) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

State the rules that make a struct automatically eligible for `Sendable`. Explain what `@unchecked Sendable` promises and who is responsible for keeping that promise. Describe how a background actor could hand an immutable snapshot to a UI model without sharing mutable state.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): Sendable types are introduced in the book's Concurrency chapter; the standard library reference documents the `Sendable` protocol and its checking rules.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-033: Sendable and strict concurrency boundaries.
Read courses/swift/guides/swift-033.md and courses/swift/lessons/swift-033.swift. Prerequisites: swift-032.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-033_solution.swift and
courses/swift/solutions/swift-033_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
