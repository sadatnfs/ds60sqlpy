# csharp-035: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-035_solution.cs](csharp-035_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Mutate through a view:** A span slice is a view, not a copy of the selected element. Only the middle element changes.

**Parse without allocating substrings:** The helper reads directly from the character view and validates each admitted character. The digit total is 6 and empty input totals zero.

## Reason through the six tasks

1. **Predict and explain.** Draw the backing array and slice boundaries.

2. **Guided modification.** Change the slice to cover two elements.

3. **Independent construction.** Write a synchronous span helper counting separators.

4. **Diagnose a defect.** Diagnose retaining a span across await.

5. **Boundary evidence.** Test empty and out-of-range slices and distinguish valid empty from invalid bounds.

6. **Transfer and justify.** Choose Span or Memory for a synchronous parser and an asynchronous buffer owner.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Span<T> is a view over contiguous memory. A slice describes a region without copying its elements, so writes through a mutable span change the underlying storage. ReadOnlySpan prevents mutation through that view but does not freeze other aliases. This makes ownership and lifetime central to correct use.

Span is a ref struct with restrictions that prevent it from escaping into ordinary heap objects. It cannot be retained across an await boundary. Memory<T> can represent a heap-storable region for asynchronous APIs, but its owner still controls lifetime. Optimize allocations only after measuring; a span does not improve an algorithm whose complexity is the real bottleneck.

`array.AsSpan(start, length)` creates a view. `Slice` changes the viewed interval. `ReadOnlySpan<T>` narrows write capability. Keep synchronous span logic in a helper separate from async orchestration.

ReadOnlySpan restricts this view, not every alias. A rented buffer must not be returned while a view is still in use. Bounds checking protects indices, not logical parsing rules.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
