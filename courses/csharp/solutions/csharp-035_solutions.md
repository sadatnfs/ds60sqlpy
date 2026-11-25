# csharp-035: explanation and comparison

Reference program: [csharp-035_solution.cs](csharp-035_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Mutate through a view:** A span slice is a view, not a copy of the selected element. Only the middle element changes.

**Parse without allocating substrings:** The helper reads directly from the character view and validates each admitted character. The digit total is 6 and empty input totals zero.

## Task answers

### Task 1: Predict and explain

Draw the backing array and slice boundaries.

**Written answer.** `values` holds 1, 2 and 3 at indices 0, 1 and 2. `values.AsSpan(1, 1)` starts at index 1 with length 1, so `middle[0]` is the same storage as `values[1]`. Doubling it changes the array to 1, 4, 3.

**Why it is correct.** A span is a reference to a starting element plus a length. It shares the array's memory, so a write through the span is a write to the array.

**Plausible wrong approach.** Treating the slice like `values.Skip(1).Take(1).ToArray()` predicts an unchanged array. That LINQ chain copies the element, but `AsSpan` does not copy anything.

**How to verify.** Check `values.AsSpan(1, 1)[0] == values[1]`, then set `middle[0] = 9` inside a helper and check `values[1] == 9`.

### Task 2: Guided modification

Change the slice to cover two elements.

**Written answer.** Use `Span<int> middle = values.AsSpan(1, 2);` and double each element with `for (int i = 0; i < middle.Length; i++) middle[i] *= 2;`. The array becomes 1, 4, 6.

**Why it is correct.** The second argument is a length, not an end index, so `(1, 2)` covers indices 1 and 2.

**Plausible wrong approach.** Reading the second argument as an end index and writing `AsSpan(1, 3)` asks for indices 1 through 3. The array has no index 3, so the call throws `ArgumentOutOfRangeException` before anything is doubled.

**How to verify.** Check `values.SequenceEqual(new[] { 1, 4, 6 })` and that `values[0]` is still 1.

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

**Plausible wrong approach.** `text.ToString().Split(separator).Length - 1` returns the same counts, including 0 for empty text, but it allocates a string and an array of substrings, which is what accepting a span was meant to avoid.

**How to verify.** The block checks `a,b,c` and an empty span. Add `",,"` expecting 2. To see that the span version allocates nothing, call it once to warm up, then check `GC.GetAllocatedBytesForCurrentThread()` is unchanged across a second call.

### Task 4: Diagnose a defect

Diagnose retaining a span across await.

**Written answer.** In `async Task<int> First(int[] data) { Span<int> view = data.AsSpan(); await Task.Delay(1); return view[0]; }` the compiler rejects using `view` after the `await`. Pass `Memory<int>` instead and take `.Span` only in synchronous code after the await.

**Why it is correct.** Locals that live across an `await` are stored in a heap-allocated state machine. `Span<T>` is a ref struct that may point at stack memory, so it cannot be stored on the heap.

**Plausible wrong approach.** Copying with `int[] copy = view.ToArray();` before the await compiles, but any later write goes to the copy, so the caller's buffer never changes when the method was meant to fill it.

**How to verify.** Compile the span version and read the error about preserving a `Span<int>` across `await`. The `Memory<int>` version that writes `memory.Span[0] = 9` after the await changes `data[0]` to 9.

### Task 5: Boundary evidence

Test empty and out-of-range slices and distinguish valid empty from invalid bounds.

**Written answer.** With `int[] values = { 1, 2, 3 }`, check `values.AsSpan(3, 0).IsEmpty` is a valid empty slice at the end, and that `values.AsSpan(4, 0)` and `values.AsSpan(2, 2)` throw `ArgumentOutOfRangeException`. Also check `SumDigits(ReadOnlySpan<char>.Empty) == 0`.

**Why it is correct.** A slice is valid when `start <= Length` and `start + length <= Length`. Start 3 with length 0 satisfies both; start 4 and the end index 4 of `(2, 2)` do not.

**Plausible wrong approach.** A guard such as `if (start >= values.Length) throw` rejects `(3, 0)`, yet that empty slice is exactly what slicing the remainder after a final separator produces, so a parser using the guard fails on input ending with a comma.

**How to verify.** Run the empty-slice check and catch `ArgumentOutOfRangeException` for the two invalid calls.

### Task 6: Transfer and justify

Choose Span or Memory for a synchronous parser and an asynchronous buffer owner.

**Written answer.** The synchronous parser takes `ReadOnlySpan<char>`, so it accepts strings, arrays and `stackalloc` buffers without copying. The asynchronous owner rents a `byte[]` from `ArrayPool<byte>.Shared`, exposes it as `Memory<byte>` to `Stream.ReadAsync`, and returns it to the pool in `Dispose`.

**Why it is correct.** `Memory<T>` can be stored in fields and survive an `await`, which `Span<T>` cannot. Having one class own the rented array gives one clear point where it is returned.

**Plausible wrong approach.** Returning the rented array to the pool in a `finally` while a stored `Memory<byte>` still refers to it lets the next `Rent` hand the same array to another caller, so two components write into one buffer.

**How to verify.** Parse `"42"` from a string and from `stackalloc char[] { '4', '2' }` and check both give 42. For the owner, read a known `MemoryStream` through `owner.Memory`, check the bytes, then dispose it.

## Mechanism and diagnostic reasoning

Span<T> is a view over contiguous memory. A slice describes a region without copying its elements, so writes through a mutable span change the underlying storage. ReadOnlySpan prevents mutation through that view but does not freeze other aliases. This makes ownership and lifetime central to correct use.

Span is a ref struct with restrictions that prevent it from escaping into ordinary heap objects. It cannot be retained across an await boundary. Memory<T> can represent a heap-storable region for asynchronous APIs, but its owner still controls lifetime. Optimize allocations only after measuring; a span does not improve an algorithm whose complexity is the real bottleneck.

`array.AsSpan(start, length)` creates a view. `Slice` changes the viewed interval. `ReadOnlySpan<T>` narrows write capability. Keep synchronous span logic in a helper separate from async orchestration.

ReadOnlySpan restricts this view, not every alias. A rented buffer must not be returned while a view is still in use. Bounds checking protects indices, not logical parsing rules.

## Review before continuing

Run the reference and confirm it prints `csharp-035: passed`, then rerun the guide's counterexample.
