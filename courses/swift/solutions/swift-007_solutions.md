# swift-007: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-007_solution.swift](swift-007_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Accumulate a total:** Before each iteration, total summarizes exactly the values already visited. The total is 12 and the empty total is zero.

**Stop at the first match:** The break encodes first-match semantics rather than accidentally returning the last match. The first 8 appears at offset 1 and 9 is absent.

## Reason through the six tasks

1. **Predict and explain.** Write the accumulator trace for every iteration.

2. **Guided modification.** Ignore negative values while preserving a stated invariant.

3. **Independent construction.** Implement a first-match search with an optional result.

4. **Diagnose a defect.** Diagnose a while loop whose progress variable never changes.

5. **Boundary evidence.** Test empty, singleton and repeated-match inputs.

6. **Transfer and justify.** Design a bounded retry loop and explain both its invariant and its stop condition.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A loop repeats a state transformation. Its invariant explains what remains true before and after every iteration. A termination argument explains why the loop eventually stops. These two ideas make a loop easier to reason about than simply reading each statement repeatedly.

For-in traversal expresses iteration over a sequence. Use enumerated when the traversal offset is useful, but do not assume that an enumerated offset is a valid index for every collection or slice. Arrays use integer indices; other collections may not. Empty input should leave the initial accumulator in a meaningful state.

`for value in values` traverses elements. `for (offset, value) in values.enumerated()` adds a traversal counter. `break` stops the loop; `continue` skips the remaining body. A while loop needs an explicit progress step.

An enumerated offset is not universally a collection index. A not-found sentinel should never be used as an index. Mutating traversal state in several places makes termination difficult to establish.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
