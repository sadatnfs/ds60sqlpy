# rust-014: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-014_solution.rs](rust-014_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Keep zero distinct from missing:** Absence is a separate case, not a special numeric value. A measured zero remains present and transforms to one.

**Propagate absence until a boundary:** The fallback is not inserted into the collection and should not be mistaken for a valid measurement. An absent lookup stays absent until the explicit display fallback.

## Reason through the six tasks

1. **Predict and explain.** Predict mapping Some(0) and None.

2. **Guided modification.** Render missing data as an unknown label instead of a numeric sentinel.

3. **Independent construction.** Write a first-valid-item lookup returning Option.

4. **Diagnose a defect.** Diagnose unwrap on an ordinary not-found path.

5. **Boundary evidence.** Test empty collections, present zero and out-of-range lookup.

6. **Transfer and justify.** Choose when absence should remain optional and when it should become a domain error.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Option represents either Some(value) or None. It is appropriate when absence is an expected outcome, such as a lookup finding no record. A real zero remains Some(0), keeping it distinct from missing information. This type-level distinction prevents sentinel values from leaking into valid calculations.

Unwrap asserts that absence is impossible and panics otherwise. Use it only when a nearby invariant or authored fixture makes that claim clear. Pattern matching, map and and_then let code retain absence through transformations until a boundary deliberately chooses a fallback. Choosing a default too early can erase information the caller needs.

`Option<T>` carries a present T or absence. `if let Some(value)` handles the present case. map transforms a present value; and_then chains an operation already returning Option. unwrap_or supplies a deliberate fallback.

None does not explain a failure reason; use Result when a reason matters. A default can hide missing data. Avoid converting every optional to a panic merely to shorten control flow.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
