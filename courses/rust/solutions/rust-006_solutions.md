# rust-006: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-006_solution.rs](rust-006_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Maintain a sum invariant:** The loop changes only its accumulator, not the source ownership. The borrowed traversal totals twelve and retains the vector.

**Find the first position:** Position stops at the first matching element rather than returning the last repeated match. The first match is position one and absence stays explicit.

## Reason through the six tasks

1. **Predict and explain.** Write the accumulator before and after every iteration.

2. **Guided modification.** Skip negative values while preserving a clear invariant.

3. **Independent construction.** Implement a first-match search with Option output.

4. **Diagnose a defect.** Diagnose an inclusive loop bound used as an array index.

5. **Boundary evidence.** Test empty, singleton and repeated-match sequences.

6. **Transfer and justify.** Design a bounded retry loop and state both its progress measure and its effect policy.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A loop repeats a state transition. An invariant explains what remains true, and a termination argument explains why repetition stops. For a sum, the accumulator equals the values already processed. For a search, the inspected prefix contains no earlier match before the chosen result.

For-in consumes an iterable, so ownership of the sequence or its borrowed view matters. Iterating an array of small Copy values can look similar to borrowing a vector, but the types determine what remains available. Use iterator adapters when they expose intent, and use an explicit loop when intermediate state or early exits need explanation.

`for value in &values` borrows elements. `enumerate` supplies traversal positions. `break` exits a loop, and loop itself can return a value through break value. An exclusive range uses `0..n`.

An iterator can consume values or borrow them depending on its construction. A position is not automatically a valid index in a different collection. Avoid unbounded loops without a deliberate stop and cancellation policy.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
