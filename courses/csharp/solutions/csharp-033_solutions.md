# csharp-033: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-033_solution.cs](csharp-033_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Protect increments:** The lock protects the read-modify-write transition, so the expected count does not depend on scheduling. Four tasks produce exactly 400 increments.

**Protect a multi-field invariant:** A synchronized writer with an unsynchronized reader does not establish the same contract. The reader uses the same gate as mutation.

## Reason through the six tasks

1. **Predict and explain.** Decompose an increment into its logical steps.

2. **Guided modification.** Increase task count while keeping the exact expected total.

3. **Independent construction.** Implement a locked transfer preserving the sum of two balances.

4. **Diagnose a defect.** Describe a two-lock acquisition cycle and repair it with an ordering rule.

5. **Boundary evidence.** Test zero operations and concurrent readers.

6. **Transfer and justify.** Choose immutable snapshots or a lock for a shared report cache and justify the ownership model.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Concurrency permits operations to overlap. A data race occurs when unsynchronized access to shared mutable state violates the required memory and ordering rules. Even an apparently simple increment includes read, calculation and write, so it is not automatically atomic. Correctness requires protecting the entire invariant, not just individual fields.

A lock establishes mutual exclusion and ordering for code using the same lock object. Keep the protected region small and avoid awaiting while holding a synchronous lock. Never choose a publicly accessible object or a mutable value as the lock identity. Deadlock is a separate risk when multiple locks are acquired in conflicting orders; a single documented ordering can prevent that class of cycle.

`lock (gate)` enters a protected region and exits even on exceptions. All accesses participating in the invariant must use the same gate. Task.WhenAll observes the completion of the scheduled work.

A passing unsynchronized stress run does not prove absence of races. Locking a different object in the reader does not protect the writer invariant. Never await inside a synchronous lock.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
