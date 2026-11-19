# swift-023: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-023_solution.swift](swift-023_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Round-trip a value model:** Value equality checks the data meaning rather than incidental JSON property ordering. The modeled fields round-trip through JSON.

**Reject a decoded domain violation:** Structural decoding and domain admission are separate responsibilities. Valid JSON can still describe an invalid item.

## Task answers

### Task 1: Predict and explain

State what the round-trip check proves.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Value equality checks the data meaning rather than incidental JSON property ordering. The modeled fields round-trip through JSON.

### Task 2: Guided modification

Add an optional description field and test missing versus present data.

No separate reference answer has been written for this task. Start from Example B: Structural decoding and domain admission are separate responsibilities. Valid JSON can still describe an invalid item.

### Task 3: Independent construction

Write a decoder that validates before returning a trusted item.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
enum DecodeError: Error {
  case invalid
}
func trustedItem(from data: Data) throws -> Item {
  let item = try JSONDecoder().decode(Item.self, from: data)
  guard item.isValid else { throw DecodeError.invalid }
  return item
}
let good = try trustedItem(from: Data(#"{"name":"pear","quantity":2}"#.utf8))
precondition(good.quantity == 2)
var rejected = false
do {
  _ = try trustedItem(from: Data(#"{"name":"pear","quantity":-1}"#.utf8))
} catch DecodeError.invalid {
  rejected = true
}
precondition(rejected)
```

**Observe:** The valid item is returned; quantity -1 decodes but is rejected before it is trusted.

Decoding proves only the shape; the validation step runs before the function returns, so callers never receive an invalid Item.

### Task 4: Diagnose a defect

Diagnose assuming synthesized Codable enforces business invariants.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: JSON key order is not a semantic equality rule. Defaults can hide missing required information. Do not decode directly into a complex object with side effects.

### Task 5: Boundary evidence

Test malformed JSON, missing required fields and unknown fields.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Round-trip a value model) and Example B (Reject a decoded domain violation).

### Task 6: Transfer and justify

Plan migration of a renamed field without discarding existing saved records.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Codable**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Codable combines encoding and decoding capabilities. The compiler can synthesize conformance for suitable value models, but successful decoding proves only the representational contract. A negative quantity can still decode into an Int. Apply domain validation after structural decoding and before admitting the value to application state.

Schema evolution needs explicit choices about renamed fields, defaults and versions. CodingKeys controls mapping between external names and internal properties. Do not expose internal state merely because automatic synthesis makes it easy. Keep transport models small and separate from resource-owning or secret-bearing objects.

JSONEncoder produces Data; JSONDecoder reconstructs a Codable type. CodingKeys maps property names. A DecodingError describes a structural mismatch, while domain validation has its own error policy.

JSON key order is not a semantic equality rule. Defaults can hide missing required information. Do not decode directly into a complex object with side effects.

## Review before continuing

Run the reference and confirm that it prints `swift-023: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
