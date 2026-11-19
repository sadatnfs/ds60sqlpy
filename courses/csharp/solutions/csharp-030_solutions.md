# csharp-030: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-030_solution.cs](csharp-030_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Observe a requested cancellation:** Calling Cancel changes request state; the explicit observation is what changes the operation control flow. The token check acknowledges cancellation.

**Cancel waiting while work remains live:** This deterministic distinction prevents treating an interrupted observer as proof that an operation never happened. The wait cancels, then the original task later completes with 9.

## Task answers

### Task 1: Predict and explain

Identify the request, observation and completion events.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Calling Cancel changes request state; the explicit observation is what changes the operation control flow. The token check acknowledges cancellation.

### Task 2: Guided modification

Pass a token through a helper and check it before a state change.

No separate reference answer has been written for this task. Start from Example B: This deterministic distinction prevents treating an interrupted observer as proof that an operation never happened. The wait cancels, then the original task later completes with 9.

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

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A catch for OperationCanceledException should match the intended cancellation policy. Cancelling a waiter does not dispose all resources owned by the operation. Retain and observe tasks that may still complete.

### Task 5: Boundary evidence

Test cancellation requested before start and after successful completion.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Observe a requested cancellation) and Example B (Cancel waiting while work remains live).

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
