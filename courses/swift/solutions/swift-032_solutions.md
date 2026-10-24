# swift-032: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-032_solution.swift](swift-032_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Replay without duplicate effect:** Identity lookup and state change occur under one actor-owned transition. A repeated operation returns its receipt without applying again.

**Reject conflicting identity reuse:** Reconciliation needs payload identity as well as an operation key. A changed payload is rejected and prior state remains intact.

## Reason through the six tasks

1. **Predict and explain.** Trace effect and receipt for the first and repeated calls.

2. **Guided modification.** Apply a second unique identity and predict the total.

3. **Independent construction.** Add a read-only receipt lookup that never re-executes work.

4. **Diagnose a defect.** Diagnose applying the effect before checking the operation identity.

5. **Boundary evidence.** Test negative payloads and concurrent identical requests.

6. **Transfer and justify.** Design a durable adapter and document what actor isolation alone cannot guarantee.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

The intermediate project gives one actor ownership of operation identities and accumulated totals. Validating a payload and recording its effect together prevents duplicate application within the actor lifetime. A repeated identity with a changed payload is a conflict, not a legitimate retry.

This is deliberately an in-memory example. Actor isolation proves a concurrency boundary, but it does not provide durable transactions across process restart. A production ledger needs storage that commits the effect and receipt atomically. The distinction between source logic, runtime checks and durable system behavior should remain explicit in the project README.

An actor dictionary records identity to payload/result. A synchronous actor method validates replay and applies new work without await between its check and update. Errors preserve conflicting requests as failures.

An in-memory actor ledger loses its state after restart. Overflow and retention policy remain explicit production requirements. Do not claim exactly-once delivery from a local dictionary.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
