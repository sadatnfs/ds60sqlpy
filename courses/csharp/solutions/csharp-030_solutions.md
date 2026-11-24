# csharp-030: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-030_solution.cs](csharp-030_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Observe a requested cancellation:** Calling Cancel changes request state; the explicit observation is what changes the operation control flow. The token check acknowledges cancellation.

**Cancel waiting while work remains live:** This deterministic distinction prevents treating an interrupted observer as proof that an operation never happened. The wait cancels, then the original task later completes with 9.

## Task answers

### Task 1: Predict and explain

Identify the request, observation and completion events.

**Written answer.** In Example A, the request is `source.Cancel()`, the observation is `ThrowIfCancellationRequested()` throwing `OperationCanceledException`, and the completion is the catch block setting `observed`, after which the check runs. In Example B, the request is again `source.Cancel()`, the observation is `WaitAsync(source.Token)` throwing, and that ends only the wait. The operation itself completes later, when `completion.SetResult(9)` runs, and awaiting `completion.Task` produces 9.

**Why it is correct.** Cancellation is cooperative: requesting it only sets a flag on the token. Nothing stops until some code observes the token, and the observing code decides what ends. Completion of the underlying work is a separate event that may happen before, after or without the cancellation.

**Plausible wrong approach.** Treating `Cancel()` as the moment the work stops predicts that `completion.Task` can never finish in Example B. It does finish, because nothing that produces it observed the token.

**How to verify.** Check `completion.Task.IsCompleted` right after the cancelled wait (false) and again after `SetResult` (true). Those two values separate the observation from the completion.

### Task 2: Guided modification

Pass a token through a helper and check it before a state change.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
var state = new List<string>();
using var source = new CancellationTokenSource();
void Apply(string change, CancellationToken token) {
  token.ThrowIfCancellationRequested();
  state.Add(change);
}
Apply("first", source.Token);
source.Cancel();
bool stopped = false;
try {
  Apply("second", source.Token);
} catch (OperationCanceledException) {
  stopped = true;
}
Check(stopped && state.SequenceEqual(new[] { "first" }), "no change");
```

**Observe:** The first change is applied, the request arrives and the second call stops before adding anything, so the state holds only first.

The helper receives the token as a parameter instead of reaching for a global, and it checks the token before the state change. That ordering is the point: if cancellation has been requested, the method exits with no partial effect. A change that was already applied stays applied, because cancellation is not rollback.

**Plausible wrong approach.** Checking the token after `state.Add(change)` lets a cancelled call still mutate the state and then report cancellation, so the caller believes nothing happened when something did.

**How to verify.** Move the token check below `state.Add` and confirm the state now contains both entries even though the second call reported cancellation.

### Task 3: Independent construction

Write an operation that stops cooperatively and preserves already committed work.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
var committed = new List<int>();
using var source = new CancellationTokenSource();
void Process(int[] items, CancellationToken token) {
  foreach (int item in items) {
    token.ThrowIfCancellationRequested();
    committed.Add(item);
    if (item == 2) {
      source.Cancel();
    }
  }
}
bool stopped = false;
try {
  Process(new[] { 1, 2, 3 }, source.Token);
} catch (OperationCanceledException) {
  stopped = true;
}
Check(stopped && committed.SequenceEqual(new[] { 1, 2 }), "kept work");
```

**Observe:** Processing stops before item 3, and items 1 and 2 remain committed.

The loop checks the token before each item, so cancellation ends the work between items without undoing what was already committed.

### Task 4: Diagnose a defect

Diagnose automatically replaying a write after its waiter times out.

**Written answer.** A client sends a write, waits with a timeout, and when the wait times out it sends the same write again. The timeout ended only the waiting, as in Example B: the first write may still be running or may already have been committed. Replaying it can apply the change twice, such as two payments or a doubled stock adjustment. Retry only operations that are idempotent, for example by attaching an idempotency key that the server uses to discard repeats, or query the outcome of the first attempt before deciding to send another.

**Why it is correct.** A timeout is information about the waiter, not about the operation. Without a way to learn the real outcome, the client cannot distinguish a lost request from a slow success.

**Plausible wrong approach.** Making the timeout longer reduces how often the duplicate happens but does not remove it. Cancelling the token after the timeout does not undo work the server already committed.

**How to verify.** Model the write with a `TaskCompletionSource` and a counter: time out the wait, replay, then complete the first attempt and observe the counter at 2. With an idempotency key checked before incrementing, the same sequence leaves it at 1.

### Task 5: Boundary evidence

Test cancellation requested before start and after successful completion.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
int runs = 0;
void Work(CancellationToken token) {
  token.ThrowIfCancellationRequested();
  runs++;
}
using var early = new CancellationTokenSource();
early.Cancel();
bool refused = false;
try {
  Work(early.Token);
} catch (OperationCanceledException) {
  refused = true;
}
Check(refused && runs == 0, "cancelled before start: no work");
using var late = new CancellationTokenSource();
Work(late.Token);
late.Cancel();
Check(runs == 1, "cancellation after completion undoes nothing");
var finished = Task.FromResult(4);
Check(await finished.WaitAsync(late.Token) == 4, "completed result kept");
```

**Observe:** A token cancelled before the call prevents any work; cancelling after the work finished leaves the count at 1 and a completed task still yields 4.

Before start, the first observation of the token throws, so the operation does nothing. After completion, nobody observes the token anymore, so the request has no effect on work already done. `WaitAsync` checks whether the task is already complete before looking at the token, so a finished result is returned even with a cancelled token.

**Plausible wrong approach.** Assuming a cancelled token always produces `OperationCanceledException` predicts that the last check throws. Cancellation affects only operations that observe it while they are still running.

**How to verify.** Replace `finished` with a task from a `TaskCompletionSource` that has not completed and confirm `WaitAsync(late.Token)` now throws `OperationCanceledException`.

### Task 6: Transfer and justify

Design an operation receipt distinguishing cancelled waiting, confirmed cancellation and unknown outcome.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Cancellation token**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Cancellation is a request for cooperation. A CancellationTokenSource owns the request; its token lets operations observe it. An operation that never checks or passes the token can continue after cancellation is requested. A timeout on the caller waiting is also distinct from termination of the underlying work.

Correct ownership includes awaiting or otherwise accounting for admitted work after a timeout. Do not retry a state-changing operation merely because the result is unknown. The first operation may still complete. Use operation identity and recovery evidence for such systems. Here, a TaskCompletionSource establishes exact states without guessing how long a background task takes.

`ThrowIfCancellationRequested` reports acknowledged cancellation. `WaitAsync(token)` cancels the wait without necessarily canceling the source task. TaskCompletionSource with RunContinuationsAsynchronously avoids executing arbitrary continuations inline inside a signal setter.

A catch for OperationCanceledException should match the intended cancellation policy. Cancelling a waiter does not dispose all resources owned by the operation. Retain and observe tasks that may still complete.

## Review before continuing

Run the reference and confirm that it prints `csharp-030: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
