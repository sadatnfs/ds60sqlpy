# swift-023: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-023_solution.swift](swift-023_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Round-trip a value model:** Value equality checks the data meaning rather than incidental JSON property ordering. The modeled fields round-trip through JSON.

**Reject a decoded domain violation:** Structural decoding and domain admission are separate responsibilities. Valid JSON can still describe an invalid item.

## Task answers

### Task 1: Predict and explain

State what the round-trip check proves.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let invalid = Item(name: "", quantity: -1)
let data = try JSONEncoder().encode(invalid)
let restored = try JSONDecoder().decode(Item.self, from: data)
precondition(restored == invalid && !restored.isValid)
```

**Observe:** Even an invalid item with an empty name and -1 round-trips to an equal value.

The round-trip proves the encoder and decoder agree on the field mapping; it says nothing about whether the values satisfy business rules.

### Task 2: Guided modification

Add an optional description field and test missing versus present data.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
struct Described: Codable, Equatable {
  let name: String
  let description: String?
}
let missing = try JSONDecoder().decode(
  Described.self, from: Data(#"{"name":"pear"}"#.utf8))
precondition(missing.description == nil)
let present = try JSONDecoder().decode(
  Described.self, from: Data(#"{"name":"pear","description":"ripe"}"#.utf8))
precondition(present.description == "ripe")
```

**Observe:** Without the key, description decodes as nil; with it, description is ripe.

Synthesized Codable uses decodeIfPresent for Optional properties, so an absent key is accepted as nil while a present one is decoded normally.

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

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
let data = Data(#"{"name":"","quantity":-5}"#.utf8)
let decoded = try JSONDecoder().decode(Item.self, from: data)
precondition(decoded.name.isEmpty && decoded.quantity == -5)
precondition(!decoded.isValid)
```

**Observe:** The decoder accepts an empty name and quantity -5 without complaint, and only isValid reports the violation.

Synthesized Codable checks JSON shape and types, not business rules, so a validation step must run before the item is trusted.

### Task 5: Boundary evidence

Test malformed JSON, missing required fields and unknown fields.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
func decodes(_ json: String) -> Bool {
  (try? JSONDecoder().decode(Item.self, from: Data(json.utf8))) != nil
}
precondition(!decodes(#"{"name":"pear","#))
precondition(!decodes(#"{"name":"pear"}"#))
precondition(decodes(#"{"name":"pear","quantity":1,"color":"green"}"#))
```

**Observe:** Truncated JSON and a missing quantity fail to decode, while an unknown color field is ignored.

Malformed syntax raises a data-corrupted error and a missing required key raises keyNotFound, but synthesized decoding silently skips keys it does not model.

### Task 6: Transfer and justify

Plan migration of a renamed field without discarding existing saved records.

No single reference answer exists: several designs can satisfy this transfer task. Build yours from the task 3 answer above (Write a decoder that validates before returning a trusted item) and the mechanism described below, and state one limitation of your choice.

## Solution reasoning

**Approach.** `Item` is a `Codable`, `Equatable` struct with a computed `isValid` that requires a non-empty name and a nonnegative quantity. Example A encodes and decodes an item and compares with `==`. Example B decodes JSON with quantity -2 and checks `isValid` separately. The task 3 answer validates after decoding before returning a trusted item.

**Why it is correct.** The synthesized coding round-trips both stored fields, so the restored item equals the original regardless of key order in the JSON text. The JSON in Example B is structurally valid, so decoding succeeds and produces quantity -2, which `isValid` then rejects. An item with an empty name is also invalid. In task 3, quantity -1 decodes but is rejected before it is trusted.

**A plausible wrong approach.** Assuming that a successful `decode` means a valid item is the mistake task 4 describes; synthesized Codable checks types and required keys only. Comparing the encoded `Data` against a hand-written JSON string is another fragile check, because key order and whitespace are not part of the contract.

**How to verify.** For task 5, decode `{"name":"pear"}` and confirm it throws because quantity is missing; decode text that is not JSON and confirm it throws; add an unknown key such as `"color"` and confirm it is ignored by the synthesized decoder.

## Mechanism and diagnostic reasoning

Codable combines encoding and decoding capabilities. The compiler can synthesize conformance for suitable value models, but successful decoding proves only the representational contract. A negative quantity can still decode into an Int. Apply domain validation after structural decoding and before admitting the value to application state.

Schema evolution needs explicit choices about renamed fields, defaults and versions. CodingKeys controls mapping between external names and internal properties. Do not expose internal state merely because automatic synthesis makes it easy. Keep transport models small and separate from resource-owning or secret-bearing objects.

JSONEncoder produces Data; JSONDecoder reconstructs a Codable type. CodingKeys maps property names. A DecodingError describes a structural mismatch, while domain validation has its own error policy.

JSON key order is not a semantic equality rule. Defaults can hide missing required information. Do not decode directly into a complex object with side effects.

## Review before continuing

Run the reference and confirm that it prints `swift-023: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
