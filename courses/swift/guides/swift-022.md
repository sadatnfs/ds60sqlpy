# swift-022: ARC, weak references and retain cycles

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-021`

## Learning objectives

Design a weak delegate relationship. Then choose weak or unowned for a relationship and justify the lifetime guarantee required.

## Purpose and mental model

Automatic Reference Counting tracks strong references to class instances. When the last strong owner releases an instance, its lifetime can end. Value types do not participate as independently reference-counted objects in the same way, although they can contain references. ARC manages memory ownership, not file or task completion.

A cycle of strong references can keep objects alive even when the application no longer needs them. A weak reference does not retain its target and becomes nil when that target disappears. An unowned reference asserts a stricter lifetime relationship and can trap if that assertion is wrong. Closure capture lists need the same ownership analysis, especially when an object stores a closure that captures itself.

## Vocabulary and concepts

**ARC:** Automatic management of strong class-reference counts.

**Weak reference:** A non-owning optional reference that can become nil.

**Retain cycle:** A cycle of strong references preventing release.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`weak var owner: Owner?` is optional and non-retaining. `[weak self]` captures a non-retaining reference for an escaping closure. Identity diagrams make cycles easier to detect than guessing from deinit timing.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Observe weak lifetime

The example observes a controlled ownership boundary without retaining the target accidentally.

```swift
import Foundation

final class Owner {}
final class Parent { var child: Child? }
final class Child { weak var parent: Parent? }

@main
struct LessonMain {
    static func main() async throws {
        do {
            var owner: Owner? = Owner()
            weak var observer = owner
            precondition(observer != nil)
            owner = nil
            precondition(observer == nil)
        }
        print("swift-022: passed")
    }
}
```

**Observe:** The weak observer becomes nil after the last strong reference is removed.

### Example B: Break a parent-child cycle

The weak back-reference breaks the ownership cycle while preserving navigation when the parent exists.

```swift
import Foundation

final class Owner {}
final class Parent { var child: Child? }
final class Child { weak var parent: Parent? }

@main
struct LessonMain {
    static func main() async throws {
        do {
            var parent: Parent? = Parent()
            let child = Child()
            parent?.child = child
            child.parent = parent
            weak var observed = parent
            parent = nil
            precondition(observed == nil && child.parent == nil)
        }
        print("swift-022: passed")
    }
}
```

**Observe:** The child survives independently without retaining its parent.

## Exercises

1. **Predict and explain.** Draw strong and weak arrows in both examples.

2. **Guided modification.** Add a temporary second strong owner and predict when the weak observer clears.

3. **Independent construction.** Design a weak delegate relationship.

4. **Diagnose a defect.** Diagnose an object retaining a closure that strongly captures the same object.

5. **Boundary evidence.** Test a callback after its weak owner has disappeared.

6. **Transfer and justify.** Choose weak or unowned for a relationship and justify the lifetime guarantee required.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Weak is not a general replacement for ownership. A local strong binding can extend lifetime during observation. ARC does not cancel asynchronous work or close external resources automatically.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain ARC, Weak reference, Retain cycle without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-022: ARC, weak references and retain cycles.
Read courses/swift/guides/swift-022.md and courses/swift/lessons/swift-022.swift. Prerequisites: swift-021.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-022_solution.swift and
courses/swift/solutions/swift-022_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
