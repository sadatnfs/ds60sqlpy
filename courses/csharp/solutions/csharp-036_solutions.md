# csharp-036: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-036_solution.cs](csharp-036_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Use only admitted buffer contents:** The pool guarantees minimum capacity, not exact size or zeroed contents. Only three initialized elements contribute to the total.

**Release retained references deliberately:** The test checks controllable ownership, avoiding a flaky assumption about when garbage collection occurs. Clearing removes the application references without promising collection timing.

## Task answers

### Task 1: Predict and explain

Separate logical length from rented array length.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The pool guarantees minimum capacity, not exact size or zeroed contents. Only three initialized elements contribute to the total.

### Task 2: Guided modification

Use a different requested length while initializing exactly that region.

No separate reference answer has been written for this task. Start from Example B: The test checks controllable ownership, avoiding a flaky assumption about when garbage collection occurs. Clearing removes the application references without promising collection timing.

### Task 3: Independent construction

Write a pooled-buffer helper with finally-based return.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
int SumPooled(int count) {
  int[] buffer = ArrayPool<int>.Shared.Rent(count);
  try {
    for (int i = 0; i < count; i++) {
      buffer[i] = i + 1;
    }
    return buffer.AsSpan(0, count).ToArray().Sum();
  } finally {
    ArrayPool<int>.Shared.Return(buffer, clearArray: true);
  }
}
Check(SumPooled(4) == 10, "logical range only");
```

**Observe:** Summing the first four slots gives 10.

The rented array may be longer than requested, so the code uses only the first count slots, and finally returns the buffer on every path.

### Task 4: Diagnose a defect

Diagnose reading uninitialized pooled capacity or returning the same buffer twice.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Never assert that a weak reference must disappear immediately after a collection request. Returning a buffer while asynchronous work still uses it causes data corruption. Pooling is not inherently a performance win.

### Task 5: Boundary evidence

Test cleanup when the computation throws.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Use only admitted buffer contents) and Example B (Release retained references deliberately).

### Task 6: Transfer and justify

Decide whether pooling is justified using allocation measurements and a stated lifetime contract.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Reachability**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

The garbage collector reclaims unreachable managed objects. Reachability is not the same as usefulness: a global list or event subscription can keep an otherwise unwanted object alive. Resource cleanup still belongs to IDisposable rather than collection timing. Measure retained references before assuming the collector is malfunctioning.

ArrayPool reuses buffers to reduce allocation pressure. A rented array may be larger than requested and may contain prior data. Use only the logical length, initialize what will be read, and return exactly the borrowed array once. Clearing sensitive contents is a deliberate policy. Pooling adds ownership complexity, so it should solve a measured allocation problem.

`ArrayPool<T>.Shared.Rent(n)` grants temporary use of at least n elements. `Return` ends ownership. A try/finally protects return on failure; never expose a view after return.

Never assert that a weak reference must disappear immediately after a collection request. Returning a buffer while asynchronous work still uses it causes data corruption. Pooling is not inherently a performance win.

## Review before continuing

Run the reference and confirm that it prints `csharp-036: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
