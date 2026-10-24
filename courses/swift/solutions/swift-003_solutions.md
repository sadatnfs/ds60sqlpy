# swift-003: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-003_solution.swift](swift-003_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Observe overflow without crashing:** The flag is essential: the partial result alone cannot identify the intended mathematical sum. 255 plus one reports overflow and a wrapped partial result of zero.

**Use a numerical comparison policy:** The force unwrap is limited to authored literal fixtures known to parse; external text needs conditional handling. The floating result meets the stated tolerance and the decimal fixture retains decimal intent.

## Reason through the six tasks

1. **Predict and explain.** Predict the overflow flag and partial result.

2. **Guided modification.** Repeat the boundary with UInt8 zero minus one using the reporting operation.

3. **Independent construction.** Write checked quantity addition that returns an explicit rejected outcome.

4. **Diagnose a defect.** Diagnose ignoring the overflow flag.

5. **Boundary evidence.** Compare zero, normal and maximum-range inputs.

6. **Transfer and justify.** Choose a numeric representation and rounding policy for a price calculation.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Integer values have bounded ranges. Ordinary overflowing integer arithmetic traps in Swift, while reporting-overflow operations return both a result and an overflow flag. Wrapping operators are explicit and useful for domains such as fixed-width bit arithmetic, but usually wrong for quantities or balances.

Floating-point values approximate many decimal fractions. Compare a result according to a numerical error contract rather than expecting every decimal identity to hold exactly. Decimal can represent base-ten financial quantities more naturally, but rounding and units still require a policy. A type choice does not replace domain reasoning.

`addingReportingOverflow` returns a tuple with partialValue and overflow. `&+` explicitly wraps. `abs(actual - expected) < tolerance` expresses a simple absolute error bound appropriate only to the stated scale.

A tolerance that hides a unit error is not a numerical policy. Avoid wrapping operators for business totals unless modulo behavior is intended. Never force-unwrap untrusted numeric text.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
