# rust-010: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-010_solution.rs](rust-010_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Mutate through one explicit borrower:** The function receives mutation capability for the duration of the call. The caller retains ownership and observes the deliberate mutation.

**Mutate two proven-disjoint regions:** The standard library API establishes disjointness instead of relying on two potentially overlapping index borrows. The two slices mutate separate halves safely.

## Reason through the six tasks

1. **Predict and explain.** Trace who may access text during the mutable call.

2. **Guided modification.** Add a second mutation after the first borrow ends.

3. **Independent construction.** Write a function swapping the ends of a mutable slice safely.

4. **Diagnose a defect.** Create conflicting mutable borrows and explain the compiler diagnostic.

5. **Boundary evidence.** Test an empty slice and a split at either endpoint.

6. **Transfer and justify.** Design an API that exposes only the smallest mutable region needed by a transformation.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

An exclusive reference grants mutation while preventing conflicting access to the same storage. The common rule is either shared readers or one exclusive borrower at a time. This is a capability rule about access, not a claim that the operating system has locked memory.

Small scopes make mutation ownership easier to see. After an exclusive borrow's last use, the owner can be used again. APIs such as split_at_mut safely produce disjoint mutable regions because they establish that the regions do not overlap. Do not reach for unsafe code merely because the compiler cannot infer a relationship you have not expressed.

`&mut value` creates exclusive access and the original binding must permit mutation. A function taking &mut T may update the borrowed value but does not own its eventual destruction. split_at_mut proves disjoint slices.

An exclusive borrow is not a thread lock. More mut annotations do not solve aliasing conflicts. Prefer safe disjointness APIs to manually asserting pointer safety.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
