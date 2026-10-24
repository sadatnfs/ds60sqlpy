# rust-030: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-030_solution.rs](rust-030_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Transfer owned data:** String's ownership and Send contract make the transfer valid without shared mutation. Owned text crosses the thread boundary and returns its length.

**Check capabilities at compile time:** Compile-time capability evidence is different from a runtime stress test. The compiler accepts the declared safe capability combinations.

## Reason through the six tasks

1. **Predict and explain.** Separate ownership transfer from shared access.

2. **Guided modification.** Move a Vec into a worker and return a derived value.

3. **Independent construction.** Choose a safe shared-state type for a small concurrent counter.

4. **Diagnose a defect.** Try sending Rc across threads and explain the diagnostic rather than adding unsafe.

5. **Boundary evidence.** Test a scoped borrowed input and compare its lifetime requirement with spawn.

6. **Transfer and justify.** Document why a proposed custom type is or is not Send and Sync from its members.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Send describes whether ownership of a value can cross thread boundaries. Sync describes whether shared references can be safely used across threads, with the relationship that a shared reference to T is Send when T is Sync. These marker traits express safety properties, not performance or automatic synchronization.

Rc is single-threaded shared ownership; Arc supports concurrent reference counts. Interior-mutability types have different synchronization rules. The compiler rejects unsafe combinations, but user-defined unsafe implementations can bypass that protection only under a rigorous invariant. Prefer composing known safe types before declaring manual marker implementations.

A generic bound `T: Send` requires cross-thread transfer capability. `T: Sync` requires safe shared access. Thread spawn also imposes a lifetime requirement; Send and static solve different constraints.

Send does not mean simultaneous mutation is safe. Static does not mean allocated forever; it constrains borrowed references in the value. Never add unsafe impl solely to silence a compiler error.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
