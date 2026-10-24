# swift-023: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-023_solution.swift](swift-023_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Round-trip a value model:** Value equality checks the data meaning rather than incidental JSON property ordering. The modeled fields round-trip through JSON.

**Reject a decoded domain violation:** Structural decoding and domain admission are separate responsibilities. Valid JSON can still describe an invalid item.

## Reason through the six tasks

1. **Predict and explain.** State what the round-trip check proves.

2. **Guided modification.** Add an optional description field and test missing versus present data.

3. **Independent construction.** Write a decoder that validates before returning a trusted item.

4. **Diagnose a defect.** Diagnose assuming synthesized Codable enforces business invariants.

5. **Boundary evidence.** Test malformed JSON, missing required fields and unknown fields.

6. **Transfer and justify.** Plan migration of a renamed field without discarding existing saved records.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Codable combines encoding and decoding capabilities. The compiler can synthesize conformance for suitable value models, but successful decoding proves only the representational contract. A negative quantity can still decode into an Int. Apply domain validation after structural decoding and before admitting the value to application state.

Schema evolution needs explicit choices about renamed fields, defaults and versions. CodingKeys controls mapping between external names and internal properties. Do not expose internal state merely because automatic synthesis makes it easy. Keep transport models small and separate from resource-owning or secret-bearing objects.

JSONEncoder produces Data; JSONDecoder reconstructs a Codable type. CodingKeys maps property names. A DecodingError describes a structural mismatch, while domain validation has its own error policy.

JSON key order is not a semantic equality rule. Defaults can hide missing required information. Do not decode directly into a complex object with side effects.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
