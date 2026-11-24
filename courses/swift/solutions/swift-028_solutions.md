# swift-028: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-028_solution.swift](swift-028_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Await an asynchronous result:** The fixture introduces the call boundary without pretending a tiny calculation needs a separate thread. The awaited result is 8.

**Propagate async failure:** Suspension capability does not change the requirement to handle failure honestly. The async boundary preserves both the valid result and the domain error.

## Task answers

### Task 1: Predict and explain

Distinguish an async declaration from actual parallel execution.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
func square(_ value: Int) async -> Int { value * value }
let first = await square(2)
let second = await square(3)
precondition(first + second == 13)
async let left = square(4)
async let right = square(5)
let both = await left + right
precondition(both == 41)
```

**Observe:** The two awaited calls give 4 + 9 = 13 one after another, and the async let pair gives 16 + 25 = 41.

Marking square async only allows it to suspend; consecutive awaits still run in sequence. Concurrency appears only when async let creates child tasks that may overlap.

### Task 2: Guided modification

Await two dependent calculations in order.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
func double(_ value: Int) async -> Int { value * 2 }
let once = await double(4)
let twice = await double(once)
precondition(once == 8 && twice == 16)
```

**Observe:** The first await gives 8, and feeding it into the second gives 16.

The second call needs the first result, so it must await in order; there is nothing to run in parallel when one step depends on another.

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

**Written answer.** A semaphore wait blocks its thread until signaled. If the async work it waits for needs that same executor (for example the main actor or a one-thread pool), the work can never run to signal, and the program deadlocks. In an async context, await the work instead; the entry point here is already async, so no blocking bridge is needed.

### Task 5: Boundary evidence

Test a valid and throwing async outcome.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
func validated(_ value: Int) async throws -> Int {
  guard value >= 0 else { throw AsyncError.invalid }
  return value
}
let zero = try await validated(0)
precondition(zero == 0)
var failed = false
do { _ = try await validated(-5) } catch AsyncError.invalid { failed = true }
precondition(failed)
```

**Observe:** 0 is accepted as the boundary value, and -5 throws AsyncError.invalid.

try await checks both effects at the call site: suspension for async and propagation for throws, so the failure reaches the caller's catch unchanged.

### Task 6: Transfer and justify

Identify suspension points in an app load operation and explain what state may change around them.

No single reference answer exists: several designs can satisfy this transfer task. Build yours from the task 3 answer above (Write an async adapter that returns a validated domain value) and the mechanism described below, and state one limitation of your choice.

## Solution reasoning

**Approach.** Example A declares `double` as `async` and awaits it from the async `main`. Example B declares `validated` as `async throws`, awaits a valid call, and catches the `AsyncError.invalid` thrown for -1. The task 3 answer is an async adapter that awaits raw text and returns a validated `Quantity`.

**Why it is correct.** `await double(4)` suspends at most once and resumes with 8; nothing in the call requires another thread. For 3, the guard passes and the awaited value is 3. For -1, the guard fails, the error propagates through the `await`, and the matching catch sets `rejected`. The task 3 adapter returns `Quantity(value: 12)` after awaiting its source text.

**A plausible wrong approach.** Wrapping the async call in a `DispatchSemaphore` and calling `wait()` from synchronous code is the task 4 defect: on a constrained executor the awaited work may need the same thread that is now blocked, so the program can hang. Writing `try? await validated(-1)` would silently drop the error and lose the rejection evidence.

**How to verify.** For task 2, await `double(4)` and then `double(result)` and check 16. For task 5, check that awaiting `validated(0)` returns 0 and that the catch clause is entered only for a negative input.

## Mechanism and diagnostic reasoning

An async function can suspend while waiting for another operation. Suspension is not the same as blocking a thread, and async does not automatically make CPU work parallel. Await marks a place where the current task may pause and other work may run. This boundary matters when shared state can change.

Keep ownership of the asynchronous result explicit. An unstructured task can outlive the scope that created it, while structured child tasks have a parent lifetime. This chapter uses tiny deterministic async functions, preparing for task groups and actors. A returned value proves this fixture completed, not that every future network or storage operation is reliable.

`async` permits suspension; `await` acknowledges an async call. An async throwing method is called with try await. The entrypoint already supports async, so no semaphore or blocking bridge is needed.

Async does not promise a background thread. Do not block an executor waiting for work that needs the same executor. Retain and await meaningful results.

## Review before continuing

Run the reference and confirm that it prints `swift-028: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
