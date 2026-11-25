# swift-030: explanation and comparison

Reference program: [swift-030_solution.swift](swift-030_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Cancel before observing a check:** The loop observes cancellation state rather than guessing a scheduling delay. The task acknowledges cancellation and its completion is awaited.

**Cancellation need not prevent a result:** A cancellation request alone is not proof that an operation failed to execute. This task still returns 9 because its body does not check cancellation.

## Task answers

### Task 1: Predict and explain

Separate cancellation request from acknowledged completion.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let task = Task { () -> String in
  while !Task.isCancelled { await Task.yield() }
  return "acknowledged"
}
precondition(!task.isCancelled)
task.cancel()
precondition(task.isCancelled)
let reply = await task.value
precondition(reply == "acknowledged")
```

**Observe:** isCancelled flips to true as soon as cancel() is called, but the result acknowledged arrives only after awaiting value.

cancel() only records a request; the task observes it at its own check and finishes, and awaiting value is what confirms that completion.

### Task 2: Guided modification

Add a cancellation check before a simulated state-changing step.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
func commit(_ log: [String]) async -> [String] {
  if Task.isCancelled { return log + ["skipped write"] }
  return log + ["wrote"]
}
let task = Task { () -> [String] in
  while !Task.isCancelled { await Task.yield() }
  return await commit(["read"])
}
task.cancel()
let cancelledLog = await task.value
precondition(cancelledLog == ["read", "skipped write"])
let normalLog = await commit(["read"])
precondition(normalLog == ["read", "wrote"])
```

**Observe:** The cancelled task records read then skipped write, while an uncancelled call records read then wrote.

Checking Task.isCancelled immediately before the state-changing step stops the write when cancellation has been requested, while the earlier read is left as it was.

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

**Written answer.** Cancelling the waiter stops the caller from waiting; it does not tell you whether the write reached the store. The outcome is unknown, so a blind retry can apply the write twice. Retry only with the same operation identity against a store that deduplicates it, or first query whether that identity was committed.

### Task 5: Boundary evidence

Test cancellation before work and after an already completed result.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
let started = await withTaskGroup(of: Int.self, returning: Bool.self) { group in
  group.cancelAll()
  return group.addTaskUnlessCancelled { 1 }
}
precondition(!started)
let finished = Task { 5 }
let first = await finished.value
finished.cancel()
let again = await finished.value
precondition(first == 5 && again == 5)
```

**Observe:** Cancelling first means the child is never started, while cancelling an already finished task still returns 5.

addTaskUnlessCancelled refuses work once the group is cancelled; a completed task's result is fixed, so a late cancel has nothing to stop.

### Task 6: Transfer and justify

Design a receipt distinguishing success, confirmed cancellation and unknown outcome.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** Example A starts a task that yields in a loop until `Task.isCancelled` becomes true and then confirms with `Task.checkCancellation()`. The parent cancels and awaits the result. Example B cancels a task whose body returns 9 without checking cancellation. The task 3 answer processes items in a loop with cleanup that runs on cancellation.

**Why it is correct.** Cancellation in Swift is a flag the task must observe. In Example A the loop sees the flag, `checkCancellation` throws `CancellationError`, and the task returns true, so `acknowledged` holds. In Example B the body never checks, so it still returns 9. In task 3, when cancellation is seen before the fourth item, items 1 to 3 are done and cleanup still runs.

**A plausible wrong approach.** Assuming `task.cancel()` stops the body immediately leads to predicting that Example B returns nothing or throws; the check `value == 9` refutes it. Retrying a write whose waiter was cancelled is the task 4 defect: the original write may already have happened, so a blind retry can apply it twice.

**How to verify.** For task 5, cancel before any work and check the cleanup record, then await a task that already finished and confirm its value is unchanged by a late `cancel()`. An uncancelled task 3 run finishes both of its items.

## Mechanism and diagnostic reasoning

Task cancellation records a request that cooperative code can observe. It does not forcibly stop every instruction. A cancelled task can still return a value if it never checks cancellation. Distinguish a caller no longer wanting a result from the operation having stopped before effects occurred.

Use cancellation checks before admitting expensive work and at meaningful loop boundaries. Cleanup remains necessary on cancellation paths. Do not replay a state-changing request simply because an observer was cancelled; the first operation may have completed. The fixture observes cancellation deterministically without relying on a race between sleep durations.

Task.isCancelled inspects state and Task.checkCancellation throws CancellationError. A task handle can be cancelled and then awaited to observe its actual completion. Cancellation handlers require careful sendable state ownership.

Polling cancellation in a tight CPU loop without yielding can waste resources. A cancellation handler must not race unsafely with the operation. Preserve result identity when deciding whether replay is safe.

## Review before continuing

Run the reference and confirm it prints `swift-030: passed`, then rerun the guide's counterexample.
