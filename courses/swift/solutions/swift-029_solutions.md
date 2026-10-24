# swift-029: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-029_solution.swift](swift-029_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Collect results without assuming order:** Independent values cross the boundary, and the parent alone mutates the result array. Sorted results are deterministic despite unspecified completion order.

**Handle an empty group:** The empty path needs no special background work or timer. No admitted children produces the identity result zero.

## Reason through the six tasks

1. **Predict and explain.** Identify who owns each task and the result array.

2. **Guided modification.** Attach input indices and reconstruct submission ordering.

3. **Independent construction.** Implement bounded admission for a small list with at most two outstanding children.

4. **Diagnose a defect.** Diagnose concurrent mutation of a shared result array inside child tasks.

5. **Boundary evidence.** Test empty input and a failing child using a throwing group.

6. **Transfer and justify.** Choose a concurrency bound for an I/O workload and explain its resource basis.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A task group creates child tasks whose lifetimes remain inside the group scope. Children may finish in any order, so result collection should not accidentally depend on scheduling. If output ordering matters, include an identity or sort after collection. Structured ownership makes it possible to await all admitted work before returning.

A group is not automatically a concurrency limit. Adding a child for every element of a huge input can overwhelm memory or downstream systems. Bound admission by adding only a limited number and replacing completed work. The fixture uses three tiny tasks and explicitly avoids claiming a timing speedup.

withTaskGroup creates a scoped group. addTask admits a child. for await consumes completed child results. A child captures only sendable data crossing the concurrency boundary.

Group completion order is unspecified. Cancellation is cooperative and does not instantly kill children. Avoid unbounded child creation for large inputs.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
