# swift-012: Structures and controlled value mutation

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-011`

## Learning objectives

Build a bounded counter with private mutation. Then choose a value model for an editable form and explain how cancel can restore an earlier snapshot.

## Purpose and mental model

A struct models a value with named properties and operations. Assignment follows value semantics, making independent state snapshots straightforward when its stored members also have appropriate semantics. A mutating method explicitly changes self or its stored properties. Methods without mutating cannot silently alter a value-type instance.

Constructors should establish valid state, and operations should preserve it. Do not expose unrestricted writable fields if they allow callers to bypass the rule. A small value type can be a strong domain boundary, but wrapping a primitive without adding meaning or validation is only extra syntax.

## Vocabulary and concepts

**Struct:** A nominal value type.

**Mutating method:** An operation explicitly allowed to modify a value.

**Encapsulation:** Controlling changes through a meaningful interface.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`struct Inventory` defines a value type. `private(set)` exposes reading but restricts assignment. A `mutating func` may update stored state. An initializer can reject invalid input with a throwing or failable contract in later chapters.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Keep copied value state independent

The struct contains value state and its mutation is explicit.

```swift
import Foundation

struct Inventory { private(set) var stock: Int; mutating func reserve(_ amount: Int) -> Bool { guard amount >= 0, amount <= stock else { return false }; stock -= amount; return true } }

@main
struct LessonMain {
    static func main() async throws {
        do {
            var first = Inventory(stock: 5)
            var second = first
            precondition(second.reserve(2))
            precondition(first.stock == 5 && second.stock == 3)
            precondition(first.reserve(0))
        }
        print("swift-012: passed")
    }
}
```

**Observe:** Reserving from the copied inventory does not change the original.

### Example B: Reject without partial mutation

Checking every rejection condition before subtraction preserves failure atomicity.

```swift
import Foundation

struct Inventory { private(set) var stock: Int; mutating func reserve(_ amount: Int) -> Bool { guard amount >= 0, amount <= stock else { return false }; stock -= amount; return true } }

@main
struct LessonMain {
    static func main() async throws {
        do {
            var inventory = Inventory(stock: 3)
            precondition(!inventory.reserve(4))
            precondition(!inventory.reserve(-1))
            precondition(inventory.stock == 3)
        }
        print("swift-012: passed")
    }
}
```

**Observe:** Rejected requests retain the previous valid stock.

## Exercises

1. **Predict and explain.** Trace both inventory copies through reservation.

2. **Guided modification.** Add a validated restock operation.

3. **Independent construction.** Build a bounded counter with private mutation.

4. **Diagnose a defect.** Diagnose subtracting stock before checking the requested amount.

5. **Boundary evidence.** Test zero, exact-stock and excess reservations.

6. **Transfer and justify.** Choose a value model for an editable form and explain how cancel can restore an earlier snapshot.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A struct can contain shared class references. Private setters are useful only when methods enforce invariants. The public memberwise initializer in a small fixture is not a substitute for validating external state.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Struct, Mutating method, Encapsulation without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-012: Structures and controlled value mutation.
Read courses/swift/guides/swift-012.md and courses/swift/lessons/swift-012.swift. Prerequisites: swift-011.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-012_solution.swift and
courses/swift/solutions/swift-012_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
