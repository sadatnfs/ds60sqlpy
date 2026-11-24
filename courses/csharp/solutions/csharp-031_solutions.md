# csharp-031: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-031_solution.cs](csharp-031_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Reject immediate excess admission:** Bounded capacity is observable before work is lost or memory grows without limit. The first item is accepted and the second immediate write is refused.

**Drain after completion:** Closing admission does not discard buffered work. Completion becomes final after the reader drains it. Both admitted items are read after completion, and later writes fail.

## Task answers

### Task 1: Predict and explain

Trace channel occupancy after each operation.

**Written answer.** Example A, capacity 1: `TryWrite(4)` succeeds and occupancy is 1. `TryWrite(5)` is refused and occupancy stays 1. `ReadAsync()` removes 4 and occupancy is 0. Example B, capacity 2: `TryWrite(2)` makes it 1, `TryWrite(3)` makes it 2 and `Complete()` closes the writer while 2 items remain buffered. The loop reads 2 (occupancy 1) and 3 (occupancy 0), then ends because the channel is both empty and completed. `Completion` finishes and the later `TryWrite(9)` is refused.

**Why it is correct.** A bounded channel holds at most its capacity. Writes add, reads remove, and completion forbids further writes without discarding what is already buffered.

**Plausible wrong approach.** Assuming `Complete()` clears the buffer predicts a sum of 0 in Example B. Assuming capacity limits only reads predicts that `TryWrite(5)` succeeds in Example A.

**How to verify.** Print `channel.Reader.Count` after each operation in both examples; the numbers match the trace above.

### Task 2: Guided modification

Increase capacity and predict which immediate writes succeed.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
var channel = Channel.CreateBounded<int>(3);
var admitted = new List<bool>();
for (int i = 1; i <= 4; i++)
  admitted.Add(channel.Writer.TryWrite(i));
Check(admitted.SequenceEqual(new[] { true, true, true, false }), "cap 3");
Check(channel.Reader.Count == 3, "three items buffered");
Check(await channel.Reader.ReadAsync() == 1, "oldest item first");
```

**Observe:** With capacity 3, the first three immediate writes succeed, the fourth is refused and the reader receives 1 first.

The prediction was three successes and one refusal: with no reader running, every successful `TryWrite` occupies one slot, so the fourth write finds the channel full. The default full mode for `TryWrite` is to refuse rather than wait. Items leave in the order they were admitted.

**Plausible wrong approach.** Expecting the fourth write to wait until space frees up confuses `TryWrite` with `WriteAsync`. Expecting it to replace an older item assumes a `DropOldest` mode that was not configured.

**How to verify.** After the first read, call `TryWrite(5)` and confirm it succeeds, because reading freed one slot.

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

**Written answer.** A consumer written as `while (channel.Reader.TryRead(out var item)) Handle(item);` stops the first time the channel is momentarily empty. If the producer is still running, later items are written after the consumer has left and are never handled. An empty open channel means "nothing yet", not "nothing ever". Use `await foreach (var item in channel.Reader.ReadAllAsync())` or a `WaitToReadAsync` loop: both wait while the channel is empty and open, and end only after the writer completes and the buffer drains.

**Why it is correct.** Only the writer knows when production is finished, and it says so by calling `Complete()`. `TryRead` returning false reports the current occupancy, not that completion signal.

**Plausible wrong approach.** Adding a short delay and checking again makes the race rarer but not impossible, and it ties correctness to timing. Checking `Reader.Count == 0` has exactly the same flaw as `TryRead`.

**How to verify.** Start a consumer using the `TryRead` loop on an empty channel, then write an item and complete the writer. The item is never handled. With `ReadAllAsync`, the same sequence handles it, and `Reader.Completion` finishes.

### Task 5: Boundary evidence

Test completion with zero buffered items and with a full buffer.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
var empty = Channel.CreateBounded<int>(2);
empty.Writer.Complete();
int seen = 0;
await foreach (int value in empty.Reader.ReadAllAsync()) { seen++; }
await empty.Reader.Completion;
Check(seen == 0, "completed empty channel ends at once");
var full = Channel.CreateBounded<int>(2);
full.Writer.TryWrite(7);
full.Writer.TryWrite(8);
Check(!full.Writer.TryWrite(9), "buffer full");
full.Writer.Complete();
int sum = 0;
await foreach (int value in full.Reader.ReadAllAsync()) { sum += value; }
await full.Reader.Completion;
Check(sum == 15, "full buffer drained after completion");
```

**Observe:** Completing an empty channel ends reading immediately with no items; completing a full channel still delivers 7 and 8.

Completion means no more writes, so the reader ends once the buffer is empty. With zero buffered items, that is immediately, and `Completion` finishes without waiting for anything. With a full buffer, the two admitted items are still delivered in order, and only then does reading end. The refused write of 9 was never admitted, so it is not part of the sum.

**Plausible wrong approach.** Expecting `ReadAllAsync` to hang on the empty completed channel confuses completed with open. Expecting the full channel to lose its items on completion would make `Complete()` a discard operation, which it is not.

**How to verify.** Leave out `empty.Writer.Complete()` and observe that the empty read loop waits forever, which is why completion is the producer's explicit responsibility.

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
