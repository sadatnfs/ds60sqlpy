# rust-022: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-022_solution.rs](rust-022_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Preserve a domain category:** A caller can decide from the type rather than inspect a fragile message substring. Negative and malformed inputs remain separate variants.

**Render a safe message:** Useful diagnostics can describe the contract while avoiding unnecessary payload disclosure. The message explains the rule without repeating raw input.

## Reason through the six tasks

1. **Predict and explain.** Match each failure to its domain variant.

2. **Guided modification.** Add a maximum-quantity category.

3. **Independent construction.** Define a custom error for an importer with syntax and storage boundaries.

4. **Diagnose a defect.** Diagnose branching on a translated message string.

5. **Boundary evidence.** Test zero, malformed and out-of-range text.

6. **Transfer and justify.** Choose which layer translates an internal error into a public response and what context it may expose.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A public error type should expose categories a caller can act on. A string alone may be readable but makes structured recovery brittle. An enum can distinguish malformed input, missing resources and storage failure. Implementing Display supplies a human description while Error can preserve an underlying cause.

Translate errors at a meaningful boundary and avoid logging or wrapping the same failure at every layer. The question-mark operator can use From conversions to preserve composition. Never expose credentials or full private payloads merely to make an error verbose. Keep a small safe context such as a field name or operation stage.

Implement std::fmt::Display and std::error::Error for a domain error. map_err can translate a lower-level category. A match over the enum preserves structured decisions without parsing an error string.

A generic string loses structured recovery information. Unwrap belongs only where a nearby fixture invariant establishes success. Do not map cancellation or unknown outcomes into an ordinary empty result.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
