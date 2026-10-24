# csharp-006: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-006_solution.cs](csharp-006_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Sum with a maintained invariant:** Before each iteration, sum equals the sum of values already visited. Zero is the identity that makes the invariant true initially. The sum is 12 and the empty sum is zero.

**Locate the first match:** Stopping at the first match is part of the contract. Without break, the same loop could return the last match. The first 8 is at index 1; 9 is absent.

## Reason through the six tasks

1. **Predict and explain.** Write the accumulator value before and after every iteration in Example A.

2. **Guided modification.** Skip negative values while preserving the sum invariant.

3. **Independent construction.** Implement a first-match search returning a separate not-found representation.

4. **Diagnose a defect.** Diagnose the condition i <= values.Length using a one-element array.

5. **Boundary evidence.** Check empty, singleton, no-match and repeated-match inputs.

6. **Transfer and justify.** Design a bounded retry loop and explain both its invariant and its stopping argument.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A loop repeats a state transition. To understand it, state what is true before the first iteration and what remains true after each iteration. This repeated truth is an invariant. A second argument explains termination: some bounded quantity moves toward a stopping condition. A correct-looking body can still fail because its boundary executes once too often or never stops.

`foreach` expresses traversal of an existing sequence and usually avoids manual index bookkeeping. Use an index when the position itself matters, but relate the valid index range to the collection length. Empty inputs are especially revealing because the initial state becomes the final result without any iteration.

`for (initial; condition; update)` initializes once, checks before each body, and updates after each body. For an array of Length n, valid indices are zero through n minus one. `break` exits the loop; `continue` skips the remainder of one iteration.

Loop indices count from zero while lengths count elements. A sentinel such as -1 must be checked before indexing. Mutating a collection during enumeration can invalidate the traversal contract.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
