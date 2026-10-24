# swift-037: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-037_solution.swift](swift-037_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Apply a bounded display policy:** The wrapper enforces a deliberate display range at every assignment. Assignments are clamped into zero through ten.

**Retain valid interior values:** The projected information explains the policy without exposing mutable internal storage. A valid interior value is unchanged and the projection exposes the range.

## Reason through the six tasks

1. **Predict and explain.** Trace initialization and both setter calls.

2. **Guided modification.** Change the allowed range and update boundary tests.

3. **Independent construction.** Create a wrapper with an explicit normalization policy for a local display field.

4. **Diagnose a defect.** Explain why silently clamping a payment amount would be misleading.

5. **Boundary evidence.** Test both endpoints and one value outside each.

6. **Transfer and justify.** Choose a wrapper or explicit validation method based on whether assignment can fail meaningfully.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A property wrapper packages behavior around property storage and access. It can validate, normalize or project a reusable policy, but it should not hide surprising I/O or authorization. The wrappedValue is the property-facing interface; projectedValue can expose related information using dollar-prefixed access.

Wrapper behavior is part of the containing type's semantics. Decide whether invalid assignments are rejected, clamped or represented as an error, and make that choice visible to readers. A clamped value can be appropriate for a display control but inappropriate for financial input where silent correction hides an error.

`@propertyWrapper` marks a wrapper type. wrappedValue supplies get/set behavior. `@Clamped var level` applies it. A projectedValue is read through `$level` when declared.

A wrapper is not a substitute for validating external input. Hidden side effects make ordinary-looking assignment hard to reason about. Document projection and mutation semantics.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
