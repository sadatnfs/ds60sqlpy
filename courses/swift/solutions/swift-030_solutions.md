# swift-030: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-030_solution.swift](swift-030_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Cancel before observing a check:** The loop observes cancellation state rather than guessing a scheduling delay. The task acknowledges cancellation and its completion is awaited.

**Cancellation need not prevent a result:** A cancellation request alone is not proof that an operation failed to execute. This task still returns 9 because its body does not check cancellation.

## Task answers

### Task 1: Predict and explain

Separate cancellation request from acknowledged completion.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The loop observes cancellation state rather than guessing a scheduling delay. The task acknowledges cancellation and its completion is awaited.

### Task 2: Guided modification

Add a cancellation check before a simulated state-changing step.

No separate reference answer has been written for this task. Start from Example B: A cancellation request alone is not proof that an operation failed to execute. This task still returns 9 because its body does not check cancellation.

### Task 3: Independent construction

Write a bounded processing loop with cleanup on cancellation.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
func process(_ items: [Int], isCancelled: () -> Bool) -> (done: [Int], cleanedUp: Bool) {
  var done: [Int] = []
  var cleanedUp = false
  do {
    defer { cleanedUp = true }
    for item in items {
      if isCancelled() { break }
      done.append(item)
    }
  }
  return (done, cleanedUp)
}
var checks = 0
let stopped = process([1, 2, 3, 4, 5]) {
  checks += 1
  return checks > 3
}
precondition(stopped.done == [1, 2, 3] && stopped.cleanedUp)
let task = Task { process([1, 2]) { Task.isCancelled } }
let full = await task.value
precondition(full.done == [1, 2] && full.cleanedUp)
```

**Observe:** When cancellation is observed before the fourth item, items 1 to 3 are done and cleanup still runs; an uncancelled task finishes both items.

The loop is bounded by its input and checks for cancellation before each item; defer guarantees cleanup however the loop ends. Injecting the check keeps the test deterministic, and a real task passes Task.isCancelled.

### Task 4: Diagnose a defect

Diagnose retrying an unknown write merely because its waiter was cancelled.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Polling cancellation in a tight CPU loop without yielding can waste resources. A cancellation handler must not race unsafely with the operation. Preserve result identity when deciding whether replay is safe.

### Task 5: Boundary evidence

Test cancellation before work and after an already completed result.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Cancel before observing a check) and Example B (Cancellation need not prevent a result).

### Task 6: Transfer and justify

Design a receipt distinguishing success, confirmed cancellation and unknown outcome.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Cooperative cancellation**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Task cancellation records a request that cooperative code can observe. It does not forcibly stop every instruction. A cancelled task can still return a value if it never checks cancellation. Distinguish a caller no longer wanting a result from the operation having stopped before effects occurred.

Use cancellation checks before admitting expensive work and at meaningful loop boundaries. Cleanup remains necessary on cancellation paths. Do not replay a state-changing request simply because an observer was cancelled; the first operation may have completed. The fixture observes cancellation deterministically without relying on a race between sleep durations.

Task.isCancelled inspects state and Task.checkCancellation throws CancellationError. A task handle can be cancelled and then awaited to observe its actual completion. Cancellation handlers require careful sendable state ownership.

Polling cancellation in a tight CPU loop without yielding can waste resources. A cancellation handler must not race unsafely with the operation. Preserve result identity when deciding whether replay is safe.

## Review before continuing

Run the reference and confirm that it prints `swift-030: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
