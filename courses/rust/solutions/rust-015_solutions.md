# rust-015: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-015_solution.rs](rust-015_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Parse and validate separately:** Parsing establishes a representation; the second check enforces the domain. Malformed text and negative quantity preserve different reasons.

**Collect only explicitly accepted values:** Converting to Option is deliberate here because the separate count retains rejection evidence; a real importer may need the full reasons. Two accepted values and one rejection are accounted for.

## Reason through the six tasks

1. **Predict and explain.** Trace the success, parse-error and domain-error paths.

2. **Guided modification.** Add an application maximum quantity with a separate error category.

3. **Independent construction.** Write a function using ? to compose two fallible steps.

4. **Diagnose a defect.** Diagnose replacing every Err with zero.

5. **Boundary evidence.** Test empty, zero, negative and overflowing textual input.

6. **Transfer and justify.** Choose a public error enum and explain which internal details should remain private.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Result distinguishes Ok(value) from Err(error). It is appropriate when failure has a reason that a caller should inspect or propagate. Parsing text naturally returns a Result because malformed input is different from an ordinary missing lookup. A robust boundary should preserve the distinction between syntax failure and domain rejection.

The question-mark operator returns early with an error while continuing with the successful value. It is a control-flow shortcut with a clear type contract, not an instruction to ignore failure. The main wrapper used in this course can propagate errors to an unsuccessful process outcome. Production APIs should choose error types that expose useful categories without leaking sensitive raw input.

`Result<T,E>` carries a success type and an error type. `?` unwraps success or converts and returns an error. map_err translates an error deliberately. match handles both paths explicitly.

Calling .ok discards the error reason. A catch-all fallback can turn data loss into success. Panic is generally the wrong interface for expected invalid external input.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
