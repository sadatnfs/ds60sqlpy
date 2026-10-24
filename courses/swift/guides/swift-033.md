# swift-033: Sendable and strict concurrency boundaries

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-032`

## Learning objectives

Replace a shared mutable result class with a sendable value result. Then design data exchange between a UI model and a background actor using immutable snapshots.

## Purpose and mental model

Sendable describes values that can cross concurrency boundaries without introducing unsafe shared mutation. Immutable structs composed of sendable members are a natural fit. A mutable reference type requires a real synchronization or isolation story; adding unchecked Sendable only removes the compiler's protection and transfers responsibility to the programmer.

Swift 6 checking makes many previously implicit assumptions visible. Treat diagnostics as design feedback: identify the owner of each mutable value and the boundary across which it moves. A MainActor-isolated UI model and a background actor can exchange immutable snapshots instead of sharing writable object graphs. This is both a language rule and an architecture technique.

## Vocabulary and concepts

**Sendable:** A capability for safely crossing concurrency boundaries.

**Isolation domain:** The context owning access to mutable state.

**Snapshot:** An independent value representing state at one point.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`struct Snapshot: Sendable` declares a crossing contract. Actor calls and child tasks create concurrency boundaries. Capture immutable values and return results instead of mutating shared containers from several tasks.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Send an immutable snapshot

No mutable object identity is shared across the boundary.

```swift
import Foundation

struct Snapshot: Sendable { let name: String; let quantity: Int }

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

### Example B: Return values to the owner

Child tasks produce values instead of concurrently mutating one array.

```swift
import Foundation

struct Snapshot: Sendable { let name: String; let quantity: Int }

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

## Exercises

1. **Predict and explain.** Identify the owner of every value crossing a task boundary.

2. **Guided modification.** Add another immutable field to the snapshot.

3. **Independent construction.** Replace a shared mutable result class with a sendable value result.

4. **Diagnose a defect.** Diagnose an unchecked Sendable annotation hiding unsynchronized mutable state.

5. **Boundary evidence.** Test empty snapshots and multiple concurrent producers.

6. **Transfer and justify.** Design data exchange between a UI model and a background actor using immutable snapshots.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Sendable does not mean every operation is cheap or atomic. Unchecked conformance requires a justified invariant and tests. MainActor protects UI isolation but does not make long CPU work appropriate on that actor.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Sendable, Isolation domain, Snapshot without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
