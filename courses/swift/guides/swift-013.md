# swift-013: Classes, identity and shared state

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-012`

## Learning objectives

Choose class or struct for a shared connection coordinator and a coordinate value. Then explain whether a shared class needs synchronization before use from concurrent tasks.

## Purpose and mental model

A class models reference identity. Assigning a class instance copies a reference, so both names can observe the same mutation. This is useful for shared coordinators and resources whose identity matters, but it makes ownership and lifetime more demanding. A let binding prevents replacing the reference while still permitting mutations allowed by the object.

Inheritance lets a subclass reuse or refine behavior, but a subclass must preserve the expectations of callers using the base type. Prefer composition when the relationship is collaboration rather than a true substitutable specialization. Mark a class final when subclassing is not part of its intended contract.

## Vocabulary and concepts

**Reference identity:** The identity of one shared object instance.

**Final class:** A class that cannot be subclassed.

**Composition:** Building behavior by collaborating with contained objects.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`final class Counter` declares a reference type without subclasses. `===` compares object identity, while `==` requires an Equatable meaning. `let reference` can still call a mutating object method.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Observe shared identity

The copied reference still identifies one object, even though both bindings are constant.

```swift
import Foundation

final class Counter { private(set) var value = 0; func increment() { value += 1 } }

@main
struct LessonMain {
    static func main() async throws {
        do {
            let first = Counter()
            let second = first
            second.increment()
            precondition(first.value == 1)
            precondition(first === second)
        }
        print("swift-013: passed")
    }
}
```

**Observe:** Both names observe the same increment.

### Example B: Equal state need not mean identity

Object identity answers a different question from comparing a property value.

```swift
import Foundation

final class Counter { private(set) var value = 0; func increment() { value += 1 } }

@main
struct LessonMain {
    static func main() async throws {
        do {
            let first = Counter()
            let second = Counter()
            precondition(first.value == second.value)
            precondition(first !== second)
        }
        print("swift-013: passed")
    }
}
```

**Observe:** Two fresh counters have equal state but distinct identities.

## Exercises

1. **Predict and explain.** Draw references before and after assignment.

2. **Guided modification.** Create a separate object and mutate only one.

3. **Independent construction.** Choose class or struct for a shared connection coordinator and a coordinate value.

4. **Diagnose a defect.** Diagnose expecting class assignment to create an independent snapshot.

5. **Boundary evidence.** Test equal property values on distinct objects.

6. **Transfer and justify.** Explain whether a shared class needs synchronization before use from concurrent tasks.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Let does not make a referenced object deeply immutable. Reference semantics do not imply thread safety. Inheritance is not a general-purpose code reuse requirement.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Reference identity, Final class, Composition without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-013: Classes, identity and shared state.
Read courses/swift/guides/swift-013.md and courses/swift/lessons/swift-013.swift. Prerequisites: swift-012.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-013_solution.swift and
courses/swift/solutions/swift-013_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
