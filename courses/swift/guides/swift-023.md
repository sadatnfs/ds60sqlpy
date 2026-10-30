# swift-023: Codable and validated data boundaries

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-022`

## Learning objectives

Write a decoder that validates before returning a trusted item. Then plan migration of a renamed field without discarding existing saved records.

## Purpose and mental model

Codable combines encoding and decoding capabilities. The compiler can synthesize conformance for suitable value models, but successful decoding proves only the representational contract. A negative quantity can still decode into an Int. Apply domain validation after structural decoding and before admitting the value to application state.

Schema evolution needs explicit choices about renamed fields, defaults and versions. CodingKeys controls mapping between external names and internal properties. Do not expose internal state merely because automatic synthesis makes it easy. Keep transport models small and separate from resource-owning or secret-bearing objects.

## Vocabulary and concepts

**Codable:** The combined encoding and decoding protocol capability.

**Coding key:** A named field in an external representation.

**Schema evolution:** Maintaining meaning as stored formats change.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

JSONEncoder produces Data; JSONDecoder reconstructs a Codable type. CodingKeys maps property names. A DecodingError describes a structural mismatch, while domain validation has its own error policy.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Round-trip a value model

Value equality checks the data meaning rather than incidental JSON property ordering.

```swift
import Foundation

struct Item: Codable, Equatable {
  let name: String
  let quantity: Int
  var isValid: Bool { !name.isEmpty && quantity >= 0 }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let original = Item(name: "pear", quantity: 3)
      let data = try JSONEncoder().encode(original)
      let restored = try JSONDecoder().decode(Item.self, from: data)
      precondition(restored == original)
    }
    print("swift-023: passed")
  }
}
```

**Observe:** The modeled fields round-trip through JSON.

### Example B: Reject a decoded domain violation

Structural decoding and domain admission are separate responsibilities.

```swift
import Foundation

struct Item: Codable, Equatable {
  let name: String
  let quantity: Int
  var isValid: Bool { !name.isEmpty && quantity >= 0 }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let data = Data("{\"name\":\"pear\",\"quantity\":-2}".utf8)
      let decoded = try JSONDecoder().decode(Item.self, from: data)
      precondition(!decoded.isValid)
      precondition(!Item(name: "", quantity: 1).isValid)
    }
    print("swift-023: passed")
  }
}
```

**Observe:** Valid JSON can still describe an invalid item.

## Exercises

1. **Predict and explain.** State what the round-trip check proves.

2. **Guided modification.** Add an optional description field and test missing versus present data.

3. **Independent construction.** Write a decoder that validates before returning a trusted item.

4. **Diagnose a defect.** Diagnose assuming synthesized Codable enforces business invariants.

5. **Boundary evidence.** Test malformed JSON, missing required fields and unknown fields.

6. **Transfer and justify.** Plan migration of a renamed field without discarding existing saved records.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

JSON key order is not a semantic equality rule. Defaults can hide missing required information. Do not decode directly into a complex object with side effects.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Codable, Coding key, Schema evolution without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-023: Codable and validated data boundaries.
Read courses/swift/guides/swift-023.md and courses/swift/lessons/swift-023.swift. Prerequisites: swift-022.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-023_solution.swift and
courses/swift/solutions/swift-023_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
