# csharp-035: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-035_solution.cs](csharp-035_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Mutate through a view:** A span slice is a view, not a copy of the selected element. Only the middle element changes.

**Parse without allocating substrings:** The helper reads directly from the character view and validates each admitted character. The digit total is 6 and empty input totals zero.

## Task answers

### Task 1: Predict and explain

Draw the backing array and slice boundaries.

No separate reference answer has been written for this task. Example A is the evidence to compare with: A span slice is a view, not a copy of the selected element. Only the middle element changes.

### Task 2: Guided modification

Change the slice to cover two elements.

No separate reference answer has been written for this task. Start from Example B: The helper reads directly from the character view and validates each admitted character. The digit total is 6 and empty input totals zero.

### Task 3: Independent construction

Write a synchronous span helper counting separators.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
int CountSeparators(ReadOnlySpan<char> text, char separator) {
  int count = 0;
  foreach (char ch in text) {
    if (ch == separator) {
      count++;
    }
  }
  return count;
}
Check(CountSeparators("a,b,c".AsSpan(), ',') == 2, "two separators");
Check(CountSeparators(ReadOnlySpan<char>.Empty, ',') == 0, "empty span");
```

**Observe:** a,b,c has two separators and an empty span has none.

The helper is synchronous and only reads the span, so the borrowed text cannot escape the call.

### Task 4: Diagnose a defect

Diagnose retaining a span across await.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: ReadOnlySpan restricts this view, not every alias. A rented buffer must not be returned while a view is still in use. Bounds checking protects indices, not logical parsing rules.

### Task 5: Boundary evidence

Test empty and out-of-range slices and distinguish valid empty from invalid bounds.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Mutate through a view) and Example B (Parse without allocating substrings).

### Task 6: Transfer and justify

Choose Span or Memory for a synchronous parser and an asynchronous buffer owner.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Span**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Span<T> is a view over contiguous memory. A slice describes a region without copying its elements, so writes through a mutable span change the underlying storage. ReadOnlySpan prevents mutation through that view but does not freeze other aliases. This makes ownership and lifetime central to correct use.

Span is a ref struct with restrictions that prevent it from escaping into ordinary heap objects. It cannot be retained across an await boundary. Memory<T> can represent a heap-storable region for asynchronous APIs, but its owner still controls lifetime. Optimize allocations only after measuring; a span does not improve an algorithm whose complexity is the real bottleneck.

`array.AsSpan(start, length)` creates a view. `Slice` changes the viewed interval. `ReadOnlySpan<T>` narrows write capability. Keep synchronous span logic in a helper separate from async orchestration.

ReadOnlySpan restricts this view, not every alias. A rented buffer must not be returned while a view is still in use. Bounds checking protects indices, not logical parsing rules.

## Review before continuing

Run the reference and confirm that it prints `csharp-035: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
