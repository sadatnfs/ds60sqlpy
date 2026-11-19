# csharp-034: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-034_solution.cs](csharp-034_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Count atomically:** Each increment is one supported atomic operation rather than a compound unsynchronized expression. The atomic count is exactly 400.

**Update one key safely:** The update delegate is a pure calculation, so repeated evaluation cannot duplicate an external effect. Twenty admitted updates produce 20.

## Task answers

### Task 1: Predict and explain

Compare count++ with Interlocked.Increment.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Each increment is one supported atomic operation rather than a compound unsynchronized expression. The atomic count is exactly 400.

### Task 2: Guided modification

Add a second independently counted key.

No separate reference answer has been written for this task. Start from Example B: The update delegate is a pure calculation, so repeated evaluation cannot duplicate an external effect. Twenty admitted updates produce 20.

### Task 3: Independent construction

Build a concurrent frequency counter using pure update functions.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
var counts = new ConcurrentDictionary<string, int>();
string[] words = { "a", "b", "a", "a" };
int Next(string key, int before) => before + 1;
Task Add(string w) => Task.Run(() => counts.AddOrUpdate(w, 1, Next));
await Task.WhenAll(words.Select(Add));
Check(counts["a"] == 3 && counts["b"] == 1, "concurrent frequencies");
```

**Observe:** a is counted 3 times and b once.

AddOrUpdate may retry the update function under contention, so the function is pure: it computes the new count from the old one without side effects.

### Task 4: Diagnose a defect

Diagnose sending a message inside an AddOrUpdate delegate.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Concurrent containers protect their own structure, not arbitrary objects stored inside them. Do not infer once-only callback execution. Use a higher-level lock or transaction for multi-location invariants.

### Task 5: Boundary evidence

Test absent and already-present keys.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Count atomically) and Example B (Update one key safely).

### Task 6: Transfer and justify

Explain why atomically updating two separate balances does not preserve a transfer invariant.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Interlocked**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Interlocked provides atomic operations on supported locations, such as increment and compare-exchange. These operations are useful for simple shared state, but several individually atomic operations do not automatically form one atomic transaction. Match the mechanism to the complete invariant.

Concurrent collections make their documented operations thread-safe. Delegates passed to GetOrAdd or AddOrUpdate may execute more than once and outside internal locks. They should therefore avoid irreversible side effects. A dictionary value being safely published does not make a mutable object stored inside it automatically thread-safe.

`Interlocked.Increment(ref value)` atomically updates one location. ConcurrentDictionary manages concurrent lookup/update operations. A factory must tolerate repeated evaluation.

Concurrent containers protect their own structure, not arbitrary objects stored inside them. Do not infer once-only callback execution. Use a higher-level lock or transaction for multi-location invariants.

## Review before continuing

Run the reference and confirm that it prints `csharp-034: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
