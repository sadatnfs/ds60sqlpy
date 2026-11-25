# csharp-029: explanation and comparison

Reference program: [csharp-029_solution.cs](csharp-029_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Await values explicitly:** The task handle and the eventual integer are distinct values even when this fixture completes immediately. Await yields 7 and confirms successful completion.

**Compose and observe failure:** Awaiting establishes ownership of both success and failure instead of losing an unobserved background result. WhenAll retains input order and await exposes the task exception.

## Task answers

### Task 1: Predict and explain

Distinguish the Task<int> handle from its awaited integer.

**Written answer.** `pending` is a `Task<int>`: a handle that represents an operation and its eventual outcome, which may be success with a value, failure or cancellation. `value` is the `int` 7 obtained by awaiting that handle. The handle can be stored, passed around, combined with other tasks and inspected with properties such as `IsCompletedSuccessfully`; the integer is just the result and carries no information about how it was produced.

**Why it is correct.** `await` unwraps the task: it waits for completion, rethrows a stored exception if the task failed and otherwise produces the result. Before the await you hold a promise; after it you hold the value.

**Plausible wrong approach.** Writing `int value = pending;` does not compile, and `pending.Result` blocks the thread and wraps a failure in `AggregateException`. Treating the task as the number confuses the operation with its outcome.

**How to verify.** Print `pending.GetType()` and `value.GetType()` and compare. Then replace `Task.FromResult(7)` with `Task.FromException<int>(new InvalidOperationException())` and confirm the await throws instead of producing a number.

### Task 2: Guided modification

Combine three completed tasks and predict output ordering.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
var tasks =
    new[] { Task.FromResult(5), Task.FromResult(1), Task.FromResult(3) };
int[] values = await Task.WhenAll(tasks);
Check(values.SequenceEqual(new[] { 5, 1, 3 }), "input order kept");
Check(tasks.All(task => task.IsCompletedSuccessfully), "all completed");
```

**Observe:** WhenAll returns 5, 1, 3, the order in which the tasks were passed, not a sorted order.

The prediction is input order. `Task.WhenAll` places each result at the index of its task in the argument array, regardless of when each task finished. Here the tasks are already complete, so there is no completion order to observe at all, and the output is still not sorted by value.

**Plausible wrong approach.** Expecting 1, 3, 5 confuses the result array with sorting, and expecting the fastest result first confuses it with `Task.WhenAny`. Neither applies to `WhenAll`.

**How to verify.** Use three `TaskCompletionSource<int>` objects, pass their tasks to `WhenAll`, complete them in reverse order and confirm the awaited array is still in input order.

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

**Written answer.** `SaveAsync(item); return "saved";` starts the save and returns immediately without awaiting it. If the save fails, the exception is stored in the returned task, which nobody observes, so the caller sees `saved` for data that was never written. Any code after the call also runs before the save has finished. Await the task, `await SaveAsync(item);`, so that failure propagates and ordering is guaranteed.

**Why it is correct.** An async method reports its failure through its task. Without `await` or another observation of that task, the exception has nowhere to go, and the calling method cannot know the operation failed.

**Plausible wrong approach.** Assigning the task to a discard, `_ = SaveAsync(item);`, only silences the compiler warning; it does not observe the failure. Wrapping the call in `try/catch` without awaiting catches nothing, because the exception is not thrown at the call site.

**How to verify.** Make the save return `Task.FromException(new IOException("disk"))`. The unawaited version returns `saved`; the awaited version throws `IOException` to the caller.

### Task 5: Boundary evidence

Test successful, failed and empty WhenAll inputs.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
int[] ok = await Task.WhenAll(Task.FromResult(1), Task.FromResult(2));
Check(ok.Sum() == 3, "successful parts combined");
var problem = new InvalidOperationException("part failed");
var bad = Task.FromException<int>(problem);
bool failed = false;
try {
  await Task.WhenAll(Task.FromResult(1), bad);
} catch (InvalidOperationException error) {
  failed = error.Message == "part failed";
}
Check(failed, "failure propagated through WhenAll");
int[] none = await Task.WhenAll(Array.Empty<Task<int>>());
Check(none.Length == 0, "empty input completes with no values");
```

**Observe:** Two successful parts give 3, one failed part makes the await throw its InvalidOperationException and no tasks give an empty array.

`WhenAll` succeeds only if every input succeeds. When one input fails, the combined task fails and `await` rethrows the first stored exception, here the one created as `problem`. An empty input is not an error: there is nothing to wait for, so the combined task completes immediately with an empty array, which keeps sums and counts well-defined.

**Plausible wrong approach.** Expecting `AggregateException` from `await` confuses it with `.Wait()` or `.Result`; `await` rethrows the inner exception. Expecting the empty case to hang or throw would make callers special-case an empty batch unnecessarily.

**How to verify.** Store the combined task in a variable before awaiting it and, inside the catch, check `combined.Exception?.InnerExceptions.Count`. With two failed inputs it is 2, even though `await` threw only the first.

### Task 6: Transfer and justify

Explain when CPU work might need scheduling separately from an asynchronous I/O API.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Mechanism and diagnostic reasoning

A Task represents eventual completion, failure or cancellation. Async methods let control return to a caller while an awaited operation is incomplete. Async does not automatically mean a new thread, and awaiting a task does not block a thread in the same way as calling Wait or Result. For I/O, the goal is to avoid holding a thread idle while another system works.

Keep task ownership visible: the caller should await work whose result or failure matters. Fire-and-forget work can outlive its owner and lose exceptions. CPU-heavy work has different scheduling needs from asynchronous I/O. This chapter uses already completed and explicitly coordinated tasks so results do not depend on network access or arbitrary delays.

`async Task<int>` declares an asynchronous result. `await` obtains the completed result or rethrows the task failure. Task.WhenAll combines completion of several tasks; its result order follows the input task order, not completion order.

Async void is mainly for required event-handler signatures, not general composable methods. Blocking with Result can deadlock in synchronization contexts. Task.Run does not make a blocking external API inherently scalable.

## Review before continuing

Run the reference and confirm it prints `csharp-029: passed`, then rerun the guide's counterexample.
