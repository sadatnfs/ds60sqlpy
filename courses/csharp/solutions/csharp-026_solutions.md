# csharp-026: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-026_solution.cs](csharp-026_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Round-trip a small transport record:** Equality checks the modeled data rather than incidental property ordering in JSON text. The restored name and quantity match the original record.

**Validate after structural decoding:** Parsing answers whether the representation is understood. Validation answers whether the application may use it. Valid JSON can decode into a rejected domain value.

## Reason through the six tasks

1. **Predict and explain.** Predict what round-trip equality establishes and what it does not.

2. **Guided modification.** Add a clearly versioned optional description field.

3. **Independent construction.** Write a decoder returning explicit validation errors for missing name and negative quantity.

4. **Diagnose a defect.** Diagnose trusting default values from missing JSON fields.

5. **Boundary evidence.** Test malformed JSON, JSON null and an extra unknown field.

6. **Transfer and justify.** Design a migration from a renamed quantity field while retaining old saved records.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

JSON provides a portable syntax for values, arrays and objects; it does not define the business schema. Deserializing into a type supplies a structural mapping, but required domain rules still need validation. A missing property can become a default value, and a syntactically valid object can still be meaningless for the application.

Schema evolution requires deciding what happens when fields are added, removed or renamed. A version field and explicit migration can preserve meaning. Do not equate a successful deserialize call with a safe external object. Validate ranges and identities before admitting the object into domain logic, and avoid serializing internal secrets merely because a public property exists.

`JsonSerializer.Serialize` creates JSON text. `Deserialize<T>` maps it into T and can return null. Records provide compact transport shapes. Serialization options control naming and formatting but do not replace domain validation.

JSON text equality is sensitive to formatting and property ordering. Structural decoding does not enforce every domain invariant. Keep public transport models separate from internal objects carrying credentials or resources.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
