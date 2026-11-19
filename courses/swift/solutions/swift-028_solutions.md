# swift-028: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-028_solution.swift](swift-028_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Await an asynchronous result:** The fixture introduces the call boundary without pretending a tiny calculation needs a separate thread. The awaited result is 8.

**Propagate async failure:** Suspension capability does not change the requirement to handle failure honestly. The async boundary preserves both the valid result and the domain error.

## Task answers

### Task 1: Predict and explain

Distinguish an async declaration from actual parallel execution.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The fixture introduces the call boundary without pretending a tiny calculation needs a separate thread. The awaited result is 8.

### Task 2: Guided modification

Await two dependent calculations in order.

No separate reference answer has been written for this task. Start from Example B: Suspension capability does not change the requirement to handle failure honestly. The async boundary preserves both the valid result and the domain error.

### Task 3: Independent construction

Write an async adapter that returns a validated domain value.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
struct Quantity {
  let value: Int
}
func fetchRaw() async -> String { "12" }
func loadQuantity() async throws -> Quantity {
  let text = await fetchRaw()
  guard let value = Int(text), value >= 0 else { throw AsyncError.invalid }
  return Quantity(value: value)
}
let quantity = try await loadQuantity()
precondition(quantity.value == 12)
```

**Observe:** The adapter awaits the raw text and returns Quantity(value: 12).

The adapter is the only place raw text becomes a domain value, and it validates after the suspension point, before returning.

### Task 4: Diagnose a defect

Diagnose blocking with a semaphore to wait for async code on a constrained executor.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Async does not promise a background thread. Do not block an executor waiting for work that needs the same executor. Retain and await meaningful results.

### Task 5: Boundary evidence

Test a valid and throwing async outcome.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Await an asynchronous result) and Example B (Propagate async failure).

### Task 6: Transfer and justify

Identify suspension points in an app load operation and explain what state may change around them.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Suspension point**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

An async function can suspend while waiting for another operation. Suspension is not the same as blocking a thread, and async does not automatically make CPU work parallel. Await marks a place where the current task may pause and other work may run. This boundary matters when shared state can change.

Keep ownership of the asynchronous result explicit. An unstructured task can outlive the scope that created it, while structured child tasks have a parent lifetime. This chapter uses tiny deterministic async functions, preparing for task groups and actors. A returned value proves this fixture completed, not that every future network or storage operation is reliable.

`async` permits suspension; `await` acknowledges an async call. An async throwing method is called with try await. The entrypoint already supports async, so no semaphore or blocking bridge is needed.

Async does not promise a background thread. Do not block an executor waiting for work that needs the same executor. Retain and await meaningful results.

## Review before continuing

Run the reference and confirm that it prints `swift-028: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
