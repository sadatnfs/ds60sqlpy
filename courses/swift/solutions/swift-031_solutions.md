# swift-031: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-031_solution.swift](swift-031_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Serialize increments:** The actor owns mutation, while child tasks send requests rather than sharing a writable integer. All twenty increments are retained.

**Keep a reservation atomic within the actor:** The check and update contain no suspension, preserving the invariant as one actor operation. The second reservation is rejected without making stock negative.

## Reason through the six tasks

1. **Predict and explain.** Identify every actor-isolated read and write.

2. **Guided modification.** Add a read-only snapshot method returning a value type.

3. **Independent construction.** Implement a bounded actor-owned queue with explicit admission.

4. **Diagnose a defect.** Diagnose checking stock, awaiting another operation and then subtracting without revalidation.

5. **Boundary evidence.** Test zero and excess reservations.

6. **Transfer and justify.** Design a reservation state machine for an operation requiring external I/O before commitment.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

An actor isolates mutable state so asynchronous callers cannot directly access it without crossing the actor boundary. This prevents many data races by making ownership part of the type system. Actor methods can still contain logical races: when an operation suspends, another task may enter and change state before it resumes.

Keep a state transition synchronous inside the actor whenever possible. If an operation must await external work, revalidate assumptions after suspension or model a reservation explicitly. Actors provide isolation, not an automatic transaction across every await. Sendable describes which values can safely cross concurrency boundaries.

`actor CounterActor` owns isolated state. Calls from outside use await even when the method body itself does not suspend. Read an actor result into a local value before passing it to precondition, whose autoclosure is synchronous.

Actors do not make all multi-step workflows transactional. Await inside an invariant-sensitive operation is a reentrancy boundary. Do not use unchecked Sendable merely to silence a real ownership diagnostic.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
