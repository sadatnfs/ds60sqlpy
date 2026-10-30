# swift-010: Dictionaries, sets and stable hashing

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-009`

## Learning objectives

Build a unique sorted list of accepted inventory names. Then design a custom Hashable key using only stable identity fields.

## Purpose and mental model

A Dictionary associates unique keys with values; a Set stores unique members. Both use Hashable to narrow equality lookup. Equal values must hash consistently. A hash value is not a persistent identifier and should not be saved as an enduring key, since hashing can vary across process runs.

Dictionary lookup returns an optional, preserving the distinction between a missing key and a present zero. Output order is not a business sorting policy. Sort keys explicitly for stable presentation. When designing a custom key, use stable identity fields and avoid changing a key after it has been inserted into hashed storage.

## Vocabulary and concepts

**Hashable:** A type providing equality-compatible hashing.

**Key:** The identity used for lookup.

**Set membership:** Presence of an equivalent element without duplicates.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`[String: Int]` declares a dictionary. `counts[key, default: 0] += 1` inserts a default only for that mutation. Set.insert returns whether an element was newly inserted. sorted establishes presentation order.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Preserve absence and zero

Optional lookup prevents missing information from being confused with a stored value.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let counts = ["pear": 0]
      precondition(counts["pear"] == 0)
      precondition(counts["apple"] == nil)
    }
    print("swift-010: passed")
  }
}
```

**Observe:** Pear is present with zero and apple is absent.

### Example B: Deduplicate and order deliberately

Set semantics establish uniqueness while sorting separately establishes order.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      var tags: Set<String> = ["red"]
      precondition(!tags.insert("red").inserted)
      precondition(tags.insert("blue").inserted)
      precondition(tags.sorted() == ["blue", "red"])
    }
    print("swift-010: passed")
  }
}
```

**Observe:** Duplicate red is not inserted and sorted output is deterministic.

## Exercises

1. **Predict and explain.** Explain the optional result of each dictionary lookup.

2. **Guided modification.** Count repeated tags using the default-value subscript.

3. **Independent construction.** Build a unique sorted list of accepted inventory names.

4. **Diagnose a defect.** Diagnose persisting hashValue as a cross-run identifier.

5. **Boundary evidence.** Test missing, present-zero and duplicate keys.

6. **Transfer and justify.** Design a custom Hashable key using only stable identity fields.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Hash collisions do not mean values are equal; equality resolves them. Dictionary order should not be treated as a report contract. A default subscript can insert values during mutation, so inspect side effects.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Hashable, Key, Set membership without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-010: Dictionaries, sets and stable hashing.
Read courses/swift/guides/swift-010.md and courses/swift/lessons/swift-010.swift. Prerequisites: swift-009.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-010_solution.swift and
courses/swift/solutions/swift-010_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
