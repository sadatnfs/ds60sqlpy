# swift-009: Arrays and copy-on-write value semantics

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-008`

## Learning objectives

Build a filtered array without changing the source. Then explain what changes when array elements are mutable class instances.

## Purpose and mental model

Swift arrays are value types. Assigning an array produces a value that behaves independently when later mutated. The implementation can share backing storage until a write requires separation, a strategy called copy-on-write. The semantic promise is independent values, not a guarantee that every assignment immediately copies all bytes.

An array of class references still contains references as its element values. Copying the array separates its sequence structure but does not clone every referenced object. Keep that distinction in mind when building snapshots or undo history. Capacity is storage preparation and does not change the count of present elements.

## Vocabulary and concepts

**Value semantics:** Independent observable values after assignment and mutation.

**Copy-on-write:** Storage sharing until a mutation requires separation.

**Capacity:** Reserved storage distinct from logical count.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`[Int]` is an array type. append grows logical count; an index replaces an existing element. reserveCapacity prepares storage. ArraySlice may preserve original indices, so use its indices rather than assuming zero.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Mutate an independent array value

The language contract concerns observable behavior even if storage was initially shared.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let original = [1, 2]
      var changed = original
      changed.append(3)
      precondition(original == [1, 2])
      precondition(changed == [1, 2, 3])
    }
    print("swift-009: passed")
  }
}
```

**Observe:** Appending to the copy leaves the original unchanged.

### Example B: Do not confuse capacity and count

Capacity is a performance hint, not an index range.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      var values: [Int] = []
      values.reserveCapacity(20)
      precondition(values.count == 0)
      values.append(7)
      precondition(values.count == 1 && values[0] == 7)
    }
    print("swift-009: passed")
  }
}
```

**Observe:** Reserving twenty slots creates no logical elements.

## Exercises

1. **Predict and explain.** Predict original and changed arrays after append.

2. **Guided modification.** Replace an element in the copy and retain the original.

3. **Independent construction.** Build a filtered array without changing the source.

4. **Diagnose a defect.** Diagnose indexing a reserved but still empty array.

5. **Boundary evidence.** Test an empty slice and a slice whose startIndex is not zero.

6. **Transfer and justify.** Explain what changes when array elements are mutable class instances.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Array value semantics do not recursively clone objects. Never assume ArraySlice starts at index zero. Repeated insertions at the front can create quadratic work.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Value semantics, Copy-on-write, Capacity without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-009: Arrays and copy-on-write value semantics.
Read courses/swift/guides/swift-009.md and courses/swift/lessons/swift-009.swift. Prerequisites: swift-008.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-009_solution.swift and
courses/swift/solutions/swift-009_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
