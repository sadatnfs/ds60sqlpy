# csharp-029: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-029_solution.cs](csharp-029_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Await values explicitly:** The task handle and the eventual integer are distinct values even when this fixture completes immediately. Await yields 7 and confirms successful completion.

**Compose and observe failure:** Awaiting establishes ownership of both success and failure instead of losing an unobserved background result. WhenAll retains input order and await exposes the task exception.

## Task answers

### Task 1: Predict and explain

Distinguish the Task<int> handle from its awaited integer.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The task handle and the eventual integer are distinct values even when this fixture completes immediately. Await yields 7 and confirms successful completion.

### Task 2: Guided modification

Combine three completed tasks and predict output ordering.

No separate reference answer has been written for this task. Start from Example B: Awaiting establishes ownership of both success and failure instead of losing an unobserved background result. WhenAll retains input order and await exposes the task exception.

### Task 3: Independent construction

Write an async method returning a validated total.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
async Task<int> TotalAsync(IEnumerable<Task<int>> parts) {
  int[] values = await Task.WhenAll(parts);
  if (values.Any(value => value < 0)) {
    throw new ArgumentException("negative part");
  }
  return values.Sum();
}
var parts = new[] { Task.FromResult(2), Task.FromResult(5) };
Check(await TotalAsync(parts) == 7, "validated total");
```

**Observe:** Parts 2 and 5 produce the validated total 7.

The method awaits every part before validating, so it never sums a partially known or negative input.

### Task 4: Diagnose a defect

Diagnose forgetting to await an operation whose failure matters.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Async void is mainly for required event-handler signatures, not general composable methods. Blocking with Result can deadlock in synchronization contexts. Task.Run does not make a blocking external API inherently scalable.

### Task 5: Boundary evidence

Test successful, failed and empty WhenAll inputs.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Await values explicitly) and Example B (Compose and observe failure).

### Task 6: Transfer and justify

Explain when CPU work might need scheduling separately from an asynchronous I/O API.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Task**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A Task represents eventual completion, failure or cancellation. Async methods let control return to a caller while an awaited operation is incomplete. Async does not automatically mean a new thread, and awaiting a task does not block a thread in the same way as calling Wait or Result. For I/O, the goal is to avoid holding a thread idle while another system works.

Keep task ownership visible: the caller should await work whose result or failure matters. Fire-and-forget work can outlive its owner and lose exceptions. CPU-heavy work has different scheduling needs from asynchronous I/O. This chapter uses already completed and explicitly coordinated tasks so results do not depend on network access or arbitrary delays.

`async Task<int>` declares an asynchronous result. `await` obtains the completed result or rethrows the task failure. Task.WhenAll combines completion of several tasks; its result order follows the input task order, not completion order.

Async void is mainly for required event-handler signatures, not general composable methods. Blocking with Result can deadlock in synchronization contexts. Task.Run does not make a blocking external API inherently scalable.

## Review before continuing

Run the reference and confirm that it prints `csharp-029: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
