# rust-028: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-028_solution.rs](rust-028_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Protect concurrent increments:** The lock protects the complete read-modify-write transition, not merely its final assignment. All four hundred increments are retained.

**Protect a relationship in one value:** Grouping related state makes the invariant's synchronization boundary visible. The transfer preserves the total under one protected tuple.

## Reason through the six tasks

1. **Predict and explain.** Draw shared ownership separately from mutable access.

2. **Guided modification.** Add another worker while keeping the exact expected total.

3. **Independent construction.** Implement a locked bounded reservation operation.

4. **Diagnose a defect.** Diagnose protecting each half of a transfer with unrelated locks.

5. **Boundary evidence.** Test zero operations and an explicitly handled poisoned lock in a separate controlled case.

6. **Transfer and justify.** Choose message passing or shared locking for a service and justify the invariant owner.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Arc provides atomically reference-counted shared ownership. It does not make the stored value safely mutable by itself. Mutex provides mutually exclusive access to a protected value, and its guard releases the lock when dropped. Put the whole invariant inside that protected transition.

Several separately protected fields can still violate a relationship if updated under different locks or at different times. Lock ordering matters when several locks are involved. Keep protected work small and avoid calling unknown code while holding a lock. Poisoning reports a panic while a lock was held and requires an explicit recovery policy.

Arc::clone shares ownership rather than deep-copying the value. Mutex::lock returns a result containing a guard. Dereferencing the mutable guard grants access until its scope ends.

Arc is not a lock and clone does not copy its inner state. Holding a guard longer than needed can block unrelated work. Do not ignore poisoning without understanding whether the invariant survived.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
