# swift-019: Associated types, opaque results and existentials

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-018`

## Learning objectives

Write a generic transformation preserving the producer item type. Then choose opaque output or existential storage for an API and document the preserved relationships.

## Purpose and mental model

An associated type names a type relationship inside a protocol. A producer can declare the type of item it produces without fixing that type for every conformer. A generic consumer retains this relationship. Opaque `some` results hide a concrete implementation while preserving one consistent underlying type selected by the function.

Existential `any` values erase more concrete information and can hold different conforming types. These tools solve different problems. Use generics or opaque types when preserving relationships helps the compiler and consumer; use existentials when heterogeneous storage or runtime substitution is the intended feature. Do not choose based only on which spelling makes an error disappear.

## Vocabulary and concepts

**Associated type:** A type selected by each protocol conformance.

**Opaque type:** A hidden but consistent concrete type.

**Type erasure:** Hiding concrete type information behind an interface.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`associatedtype Item` names a conformer-selected type. `P.Item` refers to that relationship in generic code. `some Protocol` hides one concrete return type; `any Protocol` stores an existential value.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Retain a produced type

The associated type relationship survives through the generic function.

```swift
import Foundation

protocol Producer { associatedtype Item; func produce() -> Item }
struct IntegerSource: Producer { func produce() -> Int { 7 } }
func read<P: Producer>(_ producer: P) -> P.Item { producer.produce() }
func makeLabels() -> some Sequence<String> { ["a", "b"] }

@main
struct LessonMain {
    static func main() async throws {
        do {
            let source = IntegerSource()
            let value: Int = read(source)
            precondition(value == 7)
        }
        print("swift-019: passed")
    }
}
```

**Observe:** The generic consumer knows the produced value is an Int.

### Example B: Hide representation with an opaque result

The function selects one underlying result type while exposing its element relationship.

```swift
import Foundation

protocol Producer { associatedtype Item; func produce() -> Item }
struct IntegerSource: Producer { func produce() -> Int { 7 } }
func read<P: Producer>(_ producer: P) -> P.Item { producer.produce() }
func makeLabels() -> some Sequence<String> { ["a", "b"] }

@main
struct LessonMain {
    static func main() async throws {
        do {
            let labels = makeLabels()
            precondition(Array(labels) == ["a", "b"])
        }
        print("swift-019: passed")
    }
}
```

**Observe:** The caller uses sequence behavior without naming the concrete array type.

## Exercises

1. **Predict and explain.** Trace the associated Item type through read.

2. **Guided modification.** Add a String-producing conformance.

3. **Independent construction.** Write a generic transformation preserving the producer item type.

4. **Diagnose a defect.** Explain why returning unrelated concrete types from one opaque-return function is invalid.

5. **Boundary evidence.** Test empty and nonempty opaque sequences.

6. **Transfer and justify.** Choose opaque output or existential storage for an API and document the preserved relationships.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Some does not mean any arbitrary type at each return. Existential containers can lose relationships needed by generic operations. Compiler diagnostics often point to a missing type relationship rather than a missing cast.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Associated type, Opaque type, Type erasure without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-019: Associated types, opaque results and existentials.
Read courses/swift/guides/swift-019.md and courses/swift/lessons/swift-019.swift. Prerequisites: swift-018.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-019_solution.swift and
courses/swift/solutions/swift-019_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
