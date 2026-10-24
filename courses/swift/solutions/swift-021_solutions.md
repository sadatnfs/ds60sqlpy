# swift-021: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-021_solution.swift](swift-021_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Validate before returning:** Failure carries a domain category instead of masquerading as zero. Three is accepted and a negative quantity is rejected.

**Store an outcome for later inspection:** Result separates when an operation executes from when its outcome is examined. The stored outcome retains a QuantityError.

## Reason through the six tasks

1. **Predict and explain.** Trace the normal and throwing paths.

2. **Guided modification.** Distinguish malformed text from negative quantity with separate error cases.

3. **Independent construction.** Write a throwing validator for an inventory record.

4. **Diagnose a defect.** Diagnose try? used where discarding the error reason loses required evidence.

5. **Boundary evidence.** Test empty, zero and out-of-range input.

6. **Transfer and justify.** Choose Optional, throws or Result for three APIs and explain each semantic distinction.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Swift errors represent recoverable failure that a caller must acknowledge with try. A throwing function can return its normal type or throw an Error value. Catching belongs at a layer that can recover, translate or report meaningfully. A generic fallback can hide a failed operation as an ordinary empty result.

Result stores success or failure as a value, useful when an outcome must be retained or passed through another API. Optional absence and errors are different: a missing lookup may be expected, while malformed input carries a reason. Preserve those distinctions instead of force-trying external operations.

`throws` declares failure capability. `try` acknowledges a throwing call. `do/catch` handles errors. Result<Success, Failure> stores an outcome, with Failure conforming to Error.

Try! turns recoverable failure into a trap. Try? deliberately discards error detail, so use it only when absence is the intended contract. Do not catch assertion failures as ordinary input errors.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
