# swift-031: Actors and serialized state ownership

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-030`

## Learning objectives

Implement a bounded actor-owned queue with explicit admission. Then design a reservation state machine for an operation requiring external I/O before commitment.

## Purpose and mental model

An actor isolates mutable state so asynchronous callers cannot directly access it without crossing the actor boundary. This prevents many data races by making ownership part of the type system. Actor methods can still contain logical races: when an operation suspends, another task may enter and change state before it resumes.

Keep a state transition synchronous inside the actor whenever possible. If an operation must await external work, revalidate assumptions after suspension or model a reservation explicitly. Actors provide isolation, not an automatic transaction across every await. Sendable describes which values can safely cross concurrency boundaries.

## Vocabulary and concepts

**Actor isolation:** Exclusive ownership of actor state under concurrency rules.

**Reentrancy:** Other work entering an actor while an operation is suspended.

**Sendable:** A contract for values safely crossing concurrency boundaries.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`actor CounterActor` owns isolated state. Calls from outside use await even when the method body itself does not suspend. Read an actor result into a local value before passing it to precondition, whose autoclosure is synchronous.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Serialize increments

The actor owns mutation, while child tasks send requests rather than sharing a writable integer.

```swift
import Foundation

actor CounterActor { private(set) var value = 0; func increment() { value += 1 } }
actor InventoryActor { private(set) var stock: Int; init(stock: Int) { self.stock = stock }; func reserve(_ amount: Int) -> Bool { guard amount >= 0 && amount <= stock else { return false }; stock -= amount; return true } }

@main
struct LessonMain {
    static func main() async throws {
        do {
            let counter = CounterActor()
            await withTaskGroup(of: Void.self) { group in for _ in 0..<20 { group.addTask { await counter.increment() } } }
            let value = await counter.value
            precondition(value == 20)
        }
        print("swift-031: passed")
    }
}
```

**Observe:** All twenty increments are retained.

### Example B: Keep a reservation atomic within the actor

The check and update contain no suspension, preserving the invariant as one actor operation.

```swift
import Foundation

actor CounterActor { private(set) var value = 0; func increment() { value += 1 } }
actor InventoryActor { private(set) var stock: Int; init(stock: Int) { self.stock = stock }; func reserve(_ amount: Int) -> Bool { guard amount >= 0 && amount <= stock else { return false }; stock -= amount; return true } }

@main
struct LessonMain {
    static func main() async throws {
        do {
            let inventory = InventoryActor(stock: 3)
            let first = await inventory.reserve(2)
            let second = await inventory.reserve(2)
            let remaining = await inventory.stock
            precondition(first && !second && remaining == 1)
        }
        print("swift-031: passed")
    }
}
```

**Observe:** The second reservation is rejected without making stock negative.

## Exercises

1. **Predict and explain.** Identify every actor-isolated read and write.

2. **Guided modification.** Add a read-only snapshot method returning a value type.

3. **Independent construction.** Implement a bounded actor-owned queue with explicit admission.

4. **Diagnose a defect.** Diagnose checking stock, awaiting another operation and then subtracting without revalidation.

5. **Boundary evidence.** Test zero and excess reservations.

6. **Transfer and justify.** Design a reservation state machine for an operation requiring external I/O before commitment.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Actors do not make all multi-step workflows transactional. Await inside an invariant-sensitive operation is a reentrancy boundary. Do not use unchecked Sendable merely to silence a real ownership diagnostic.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Actor isolation, Reentrancy, Sendable without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-031: Actors and serialized state ownership.
Read courses/swift/guides/swift-031.md and courses/swift/lessons/swift-031.swift. Prerequisites: swift-030.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-031_solution.swift and
courses/swift/solutions/swift-031_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
