# csharp-031: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-031_solution.cs](csharp-031_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Reject immediate excess admission:** Bounded capacity is observable before work is lost or memory grows without limit. The first item is accepted and the second immediate write is refused.

**Drain after completion:** Closing admission does not discard buffered work. Completion becomes final after the reader drains it. Both admitted items are read after completion, and later writes fail.

## Task answers

### Task 1: Predict and explain

Trace channel occupancy after each operation.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Bounded capacity is observable before work is lost or memory grows without limit. The first item is accepted and the second immediate write is refused.

### Task 2: Guided modification

Increase capacity and predict which immediate writes succeed.

No separate reference answer has been written for this task. Start from Example B: Closing admission does not discard buffered work. Completion becomes final after the reader drains it. Both admitted items are read after completion, and later writes fail.

### Task 3: Independent construction

Build a bounded producer-consumer pipeline with explicit writer completion.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
var channel = Channel.CreateBounded<int>(2);
Task producer = Task.Run(async () => {
  for (int i = 1; i <= 5; i++) {
    await channel.Writer.WriteAsync(i);
  }
  channel.Writer.Complete();
});
int sum = 0;
int count = 0;
await foreach (int value in channel.Reader.ReadAllAsync()) {
  sum += value;
  count++;
}
await producer;
Check(sum == 15 && count == 5, "every item consumed once");
```

**Observe:** The consumer receives five items, 1 to 5, and the sum is 15.

WriteAsync waits while two items are buffered, and Complete tells the consumer that no more items will arrive, which ends the loop.

### Task 4: Diagnose a defect

Diagnose treating an empty open channel as permanently finished.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: An ignored false TryWrite result loses work. Blocking a producer while holding a lock needed by the consumer can deadlock. Completion and cancellation need a deliberate ownership policy.

### Task 5: Boundary evidence

Test completion with zero buffered items and with a full buffer.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Reject immediate excess admission) and Example B (Drain after completion).

### Task 6: Transfer and justify

Choose wait, reject or drop behavior for a workload and explain what evidence the producer receives.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Backpressure**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A channel connects producers and consumers through an asynchronous queue. Capacity is a resource policy: an unbounded queue can retain more work than memory or downstream systems can handle. A bounded channel makes overload visible through waiting, rejection or an explicit drop policy. Choose that policy from the value of the work, not from convenience.

Completion means no more writes will be admitted, while readers can still drain buffered items. A consumer should distinguish an empty-but-open channel from a completed channel. Cancellation and failure also need owners: somebody must complete the writer and account for admitted items. The single-process fixture teaches these states without depending on thread timing.

`Channel.CreateBounded<T>` creates a capacity-limited channel. TryWrite reports immediate admission. ReadAsync removes an item; Writer.Complete closes admission. Reader.Completion finishes after buffered work is drained.

An ignored false TryWrite result loses work. Blocking a producer while holding a lock needed by the consumer can deadlock. Completion and cancellation need a deliberate ownership policy.

## Review before continuing

Run the reference and confirm that it prints `csharp-031: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
