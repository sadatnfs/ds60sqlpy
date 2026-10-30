# swift-011: Tuples, enums and associated values

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-010`

## Learning objectives

Model loading, ready and failed states with an enum. Then choose tuple or named enum/struct for a reusable public API and explain the tradeoff.

## Purpose and mental model

A tuple groups a fixed set of values without introducing a new nominal type. It is useful for local multi-value results, but a named type is clearer when the same concept crosses several APIs. An enum represents one case from a finite set. Associated values attach data relevant only to that case.

Explicit cases prevent impossible combinations such as success=true with an error message and no result. A switch must handle the alternatives. This is a strong foundation for application state machines, parsing results and asynchronous loading state. Add a new case only when it represents a real domain distinction, then review every consumer.

## Vocabulary and concepts

**Tuple:** A fixed grouping of component values.

**Enum:** A type whose value is one declared case.

**Associated value:** Data carried by a particular enum case.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

`(count: Int, rejected: Int)` names tuple components. `enum Outcome { case value(Int); case invalid(String) }` binds case-specific payloads. `case .value(let count)` extracts only the matching payload.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Return two related counts

The grouping is useful locally without requiring an entire class hierarchy.

```swift
import Foundation

enum Outcome {
  case value(Int)
  case invalid(String)
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let summary = (accepted: 3, rejected: 2)
      precondition(summary.accepted + summary.rejected == 5)
    }
    print("swift-011: passed")
  }
}
```

**Observe:** Named tuple fields expose the accounting relationship.

### Example B: Model distinct outcomes

The switch extracts data after establishing the state case.

```swift
import Foundation

enum Outcome {
  case value(Int)
  case invalid(String)
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let outcomes: [Outcome] = [.value(4), .invalid("negative")]
      let rendered = outcomes.map { outcome in
        switch outcome {
        case .value(let count): return "count:\(count)"
        case .invalid(let reason): return "error:\(reason)"
        }
      }
      precondition(rendered == ["count:4", "error:negative"])
    }
    print("swift-011: passed")
  }
}
```

**Observe:** Each outcome exposes only its own meaningful payload.

## Exercises

1. **Predict and explain.** Name the meaning of each tuple field.

2. **Guided modification.** Add a third accounting field only if its meaning is independent.

3. **Independent construction.** Model loading, ready and failed states with an enum.

4. **Diagnose a defect.** Diagnose several optional fields that permit contradictory state combinations.

5. **Boundary evidence.** Add a new enum case and inspect the compiler-reported consumers requiring updates.

6. **Transfer and justify.** Choose tuple or named enum/struct for a reusable public API and explain the tradeoff.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

An enum raw value and an associated value solve different problems. A catch-all default can conceal a newly added state. Avoid using tuples so large that their positional relationship becomes obscure.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Tuple, Enum, Associated value without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-011: Tuples, enums and associated values.
Read courses/swift/guides/swift-011.md and courses/swift/lessons/swift-011.swift. Prerequisites: swift-010.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-011_solution.swift and
courses/swift/solutions/swift-011_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
