# swift-035: Unsafe memory, buffers and scope-limited access

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-034`

## Learning objectives

Wrap a scoped read-only buffer operation behind a safe function contract. Then write an interoperability checklist covering ownership, alignment, initialization and error reporting.

## Purpose and mental model

Swift normally protects memory through value semantics, ARC and checked collection access. Unsafe pointer APIs deliberately cross that protection boundary for interoperability and specialized performance work. A pointer is valid only while its owner guarantees storage lifetime and binding. Compiling unsafe code does not prove its memory access is valid.

Prefer scoped buffer APIs that lend a pointer only for a closure. Do not store that pointer or use it after the closure returns. Distinguish initialized elements from allocated capacity, and preserve element alignment and type binding. This lesson uses read-only scoped access to an owned array, keeping the demonstration small enough to inspect fully.

## Vocabulary and concepts

**Pointer:** An address-based view of storage with explicit lifetime obligations.

**Borrowed access:** Temporary access without taking ownership.

**Undefined behavior:** Behavior outside the guarantees of the language or memory contract.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

withUnsafeBufferPointer temporarily borrows contiguous elements. The pointer count states initialized accessible elements. Return a copied result from the closure, never the borrowed pointer itself.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Borrow only within the closure

Scoped access limits the lifetime reasoning to one visible closure.

```swift
import Foundation



@main
struct LessonMain {
    static func main() async throws {
        do {
            let values = [2, 3, 4]
            let total = values.withUnsafeBufferPointer { buffer in buffer.reduce(0, +) }
            precondition(total == 9)
        }
        print("swift-035: passed")
    }
}
```

**Observe:** The result escapes as an integer while the borrowed pointer does not.

### Example B: Handle empty storage without dereferencing

No base-address dereference is needed, avoiding assumptions about a pointer for empty storage.

```swift
import Foundation



@main
struct LessonMain {
    static func main() async throws {
        do {
            let values: [Int] = []
            let count = values.withUnsafeBufferPointer { buffer in buffer.count }
            precondition(count == 0)
        }
        print("swift-035: passed")
    }
}
```

**Observe:** An empty buffer is valid to inspect by count.

## Exercises

1. **Predict and explain.** Identify the pointer lifetime and the returned owned result.

2. **Guided modification.** Compute a maximum with an explicit empty-input policy.

3. **Independent construction.** Wrap a scoped read-only buffer operation behind a safe function contract.

4. **Diagnose a defect.** Diagnose returning the buffer baseAddress for later use.

5. **Boundary evidence.** Test empty, singleton and multi-element buffers.

6. **Transfer and justify.** Write an interoperability checklist covering ownership, alignment, initialization and error reporting.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Unsafe does not disable all runtime checks or make an operation faster. Never infer lifetime from a pointer value remaining numerically unchanged. Keep native API ownership documented and avoid unsafe code when safe collections suffice.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Pointer, Borrowed access, Undefined behavior without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-035: Unsafe memory, buffers and scope-limited access.
Read courses/swift/guides/swift-035.md and courses/swift/lessons/swift-035.swift. Prerequisites: swift-034.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-035_solution.swift and
courses/swift/solutions/swift-035_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
