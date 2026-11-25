# swift-023: Codable and validated data boundaries

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-022`

## Learning objectives

Encode and decode with Codable and validate decoded values before trusting them. The central exercise is task 3: Write a decoder that validates before returning a trusted item.

## Purpose and mental model

Codable combines encoding and decoding capabilities. The compiler can synthesize conformance for suitable value models, but successful decoding proves only the representational contract. A negative quantity can still decode into an Int. Apply domain validation after structural decoding and before admitting the value to application state.

Schema evolution needs explicit choices about renamed fields, defaults and versions. CodingKeys controls mapping between external names and internal properties. Do not expose internal state merely because automatic synthesis makes it easy. Keep transport models small and separate from resource-owning or secret-bearing objects.

## Vocabulary and concepts

**Codable:** The combined encoding and decoding protocol capability.

**Coding key:** A named field in an external representation.

**Schema evolution:** Maintaining meaning as stored formats change.

## How to run this lesson

Both examples use `JSONEncoder` and `JSONDecoder` from Foundation, which the Linux classroom provides. Decoding failures throw, and the throwing `main` would end the program, so wrap the malformed cases for task 5 in `do` and `catch` and record which `DecodingError` case each produces.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

JSONEncoder produces Data; JSONDecoder reconstructs a Codable type. CodingKeys maps property names. A DecodingError describes a structural mismatch, while domain validation has its own error policy.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

**Trace.** `original` is an `Item` with name pear and quantity 3. `JSONEncoder().encode` uses the compiler-synthesized `Codable` conformance to produce a UTF-8 JSON object with the two keys. `JSONDecoder().decode(Item.self, from:)` reads that data back and builds a new `Item`. The check uses `Equatable`, also synthesized, so it compares field values. The order of keys in the JSON text is never inspected, which is deliberate, because the encoder does not promise any particular order.

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

**Trace.** The literal JSON has both required keys with correct types, so decoding succeeds and produces an item whose quantity is -2. Synthesized `Decodable` checks structure and types only; it knows nothing about the rule that quantities are nonnegative. The `isValid` computed property expresses that rule, and it returns false. The last check shows the other half of the rule: an empty name with quantity 1 is also invalid, even though it would encode and decode without error.

## Exercises

1. **Predict and explain.** State what the round-trip check proves.

2. **Guided modification.** Add an optional description field and test missing versus present data.

3. **Independent construction.** Write a decoder that validates before returning a trusted item.

4. **Diagnose a defect.** Diagnose assuming synthesized Codable enforces business invariants.

5. **Boundary evidence.** Test malformed JSON, missing required fields and unknown fields.

6. **Transfer and justify.** Plan migration of a renamed field without discarding existing saved records.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

JSON key order is not a semantic equality rule. Defaults can hide missing required information. Do not decode directly into a complex object with side effects.

Task 4's misconception is that decoding success implies a trusted value. The counterexample is Example B's own input: quantity -2 decodes successfully, so a function that returns the decoded value directly admits it. The fix in task 3 checks `isValid` and throws when it fails. For task 5, a missing quantity throws `keyNotFound`, broken JSON throws `dataCorrupted`, and an unknown extra key is silently ignored.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Round-trip a value model) before changing anything, and confirm its observation: The modeled fields round-trip through JSON.
2. Compare Example B (Reject a decoded domain violation) with Example A and name the first line whose behavior differs. Its observation is: Valid JSON can still describe an invalid item.
3. Before opening the explanation, check your task 3 attempt (Write a decoder that validates before returning a trusted item) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain what a round-trip check proves and what it does not prove about invalid data. Say how an optional description field behaves when the key is missing versus present with null. Outline how a custom `init(from:)` could accept an old field name while writing only the new one.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The Foundation reference article Encoding and Decoding Custom Types explains synthesized Codable conformance, coding keys and custom decoding.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
