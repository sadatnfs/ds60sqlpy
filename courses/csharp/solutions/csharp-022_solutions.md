# csharp-022: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-022_solution.cs](csharp-022_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Consume only a prefix:** The producer does not need to allocate all four outputs before serving the first one. The consumer receives 5 and 6 and can stop before the full range.

**Validate before returning the sequence:** The outer method validates first; the local iterator performs only the admitted traversal. Negative count is rejected immediately, without enumeration.

## Task answers

### Task 1: Predict and explain

Trace how many values Take(2) requests.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The producer does not need to allocate all four outputs before serving the first one. The consumer receives 5 and 6 and can stop before the full range.

### Task 2: Guided modification

Generate every second integer with a bounded count.

No separate reference answer has been written for this task. Start from Example B: The outer method validates first; the local iterator performs only the admitted traversal. Negative count is rejected immediately, without enumeration.

### Task 3: Independent construction

Implement a lazy sequence of cumulative totals.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
IEnumerable<int> Cumulative(IEnumerable<int> values) {
  int total = 0;
  foreach (int value in values) {
    total = checked(total + value);
    yield return total;
  }
}
int[] totals = Cumulative(new[] { 1, 2, 3 }).ToArray();
Check(totals.SequenceEqual(new[] { 1, 3, 6 }), "running totals");
Check(!Cumulative(Array.Empty<int>()).Any(), "empty input");
```

**Observe:** 1, 2, 3 produces 1, 3, 6; an empty input produces nothing.

yield return makes the sequence lazy: each total is computed only when the consumer asks for the next element.

### Task 4: Diagnose a defect

Diagnose validation inside an iterator body that callers expect to run immediately.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: A sequence is not necessarily repeatable or cheap to enumerate. Do not assume calling an iterator method executes its body. Overflow remains possible even in a lazy generator.

### Task 5: Boundary evidence

Test count zero, one and negative.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Consume only a prefix) and Example B (Validate before returning the sequence).

### Task 6: Transfer and justify

Choose a sequence API for a large file and document repeated-enumeration and resource-lifetime behavior.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Iterator**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

An iterator describes a sequence whose values are produced as the consumer asks for them. It can avoid materializing a large collection and can stop work when the consumer stops early. `yield return` pauses the iterator with its local state retained; the next request resumes it. This is different from returning a fully constructed list.

Lazy code shifts both work and some errors into enumeration. If argument validation must happen at the call site, place it outside the iterator body and return a nested iterator. Resource-owning iterators must also release resources when enumeration is abandoned. Consumers using foreach receive disposal behavior; custom enumerator handling must preserve it.

`IEnumerable<int>` exposes an iterable sequence. `yield return value` supplies one element and suspends. A nested local iterator separates immediate argument validation from delayed generation.

A sequence is not necessarily repeatable or cheap to enumerate. Do not assume calling an iterator method executes its body. Overflow remains possible even in a lazy generator.

## Review before continuing

Run the reference and confirm that it prints `csharp-022: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
