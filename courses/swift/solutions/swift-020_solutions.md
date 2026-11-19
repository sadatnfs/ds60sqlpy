# swift-020: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-020_solution.swift](swift-020_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Use slice indices honestly:** Element count and index origin are different properties. The slice starts at index 1 while traversal still produces two elements.

**Materialize a lazy transformation:** Pure transformations keep delayed execution understandable and reproducible. The lazy recipe produces 20 and 30 when consumed.

## Task answers

### Task 1: Predict and explain

Predict slice count and startIndex separately.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Element count and index origin are different properties. The slice starts at index 1 while traversal still produces two elements.

### Task 2: Guided modification

Traverse the slice using its indices.

No separate reference answer has been written for this task. Start from Example B: Pure transformations keep delayed execution understandable and reproducible. The lazy recipe produces 20 and 30 when consumed.

### Task 3: Independent construction

Write a generic sum over Sequence where the element type is suitable.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
func sum<S: Sequence>(_ values: S) -> S.Element where S.Element: AdditiveArithmetic {
  var total = S.Element.zero
  for value in values { total += value }
  return total
}
precondition(sum([1, 2, 3]) == 6)
precondition(sum([1.5, 2.5]) == 4.0)
precondition(sum([Int]()) == 0)
```

**Observe:** The sum works for Ints (6) and Doubles (4.0) and returns 0 for an empty sequence.

AdditiveArithmetic supplies both .zero and +, which is exactly what summing needs, so any suitable element type works.

### Task 4: Diagnose a defect

Diagnose indexing a slice from zero to count minus one.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Not every Sequence can be traversed repeatedly. Index movement may be linear. Side effects in lazy closures can run later or more often than a caller expects.

### Task 5: Boundary evidence

Test an empty slice and a single-pass custom sequence.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Use slice indices honestly) and Example B (Materialize a lazy transformation).

### Task 6: Transfer and justify

Choose lazy or materialized processing for a large input and explain repeatability and memory costs.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Sequence**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Sequence promises iteration but not necessarily repeatability or efficient indexing. Collection adds reusable traversal with indices, and more specialized protocols add bidirectional or random access. Write an algorithm against the capability it needs rather than assuming every sequence behaves like an array.

Lazy transformations defer work until consumption. This can avoid intermediate storage, but it also delays side effects and errors. Keep transformation closures pure. A slice can retain original indices, so using zero-based offsets indiscriminately breaks otherwise generic code. Complexity belongs to the chosen collection and operation, not merely to its spelling.

`collection.indices` supplies valid positions. `lazy.map` creates deferred transformation. `Array(sequence)` materializes. reduce summarizes a sequence without requiring indexing.

Not every Sequence can be traversed repeatedly. Index movement may be linear. Side effects in lazy closures can run later or more often than a caller expects.

## Review before continuing

Run the reference and confirm that it prints `swift-020: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
