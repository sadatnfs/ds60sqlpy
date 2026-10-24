# swift-028: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-028_solution.swift](swift-028_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Await an asynchronous result:** The fixture introduces the call boundary without pretending a tiny calculation needs a separate thread. The awaited result is 8.

**Propagate async failure:** Suspension capability does not change the requirement to handle failure honestly. The async boundary preserves both the valid result and the domain error.

## Reason through the six tasks

1. **Predict and explain.** Distinguish an async declaration from actual parallel execution.

2. **Guided modification.** Await two dependent calculations in order.

3. **Independent construction.** Write an async adapter that returns a validated domain value.

4. **Diagnose a defect.** Diagnose blocking with a semaphore to wait for async code on a constrained executor.

5. **Boundary evidence.** Test a valid and throwing async outcome.

6. **Transfer and justify.** Identify suspension points in an app load operation and explain what state may change around them.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

An async function can suspend while waiting for another operation. Suspension is not the same as blocking a thread, and async does not automatically make CPU work parallel. Await marks a place where the current task may pause and other work may run. This boundary matters when shared state can change.

Keep ownership of the asynchronous result explicit. An unstructured task can outlive the scope that created it, while structured child tasks have a parent lifetime. This chapter uses tiny deterministic async functions, preparing for task groups and actors. A returned value proves this fixture completed, not that every future network or storage operation is reliable.

`async` permits suspension; `await` acknowledges an async call. An async throwing method is called with try await. The entrypoint already supports async, so no semaphore or blocking bridge is needed.

Async does not promise a background thread. Do not block an executor waiting for work that needs the same executor. Retain and await meaningful results.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
