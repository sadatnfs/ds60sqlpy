# swift-020: explanation and comparison

Reference program: [swift-020_solution.swift](swift-020_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Use slice indices honestly:** Element count and index origin are different properties. The slice starts at index 1 while traversal still produces two elements.

**Materialize a lazy transformation:** Pure transformations keep delayed execution understandable and reproducible. The lazy recipe produces 20 and 30 when consumed.

## Task answers

### Task 1: Predict and explain

Predict slice count and startIndex separately.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let values = [10, 20, 30, 40]
let slice = values[1...2]
precondition(slice.count == 2)
precondition(slice.startIndex == 1 && slice.endIndex == 3)
```

**Observe:** The slice has count 2 but startIndex 1 and endIndex 3.

count measures how many elements the slice holds, while startIndex is inherited from the base array, so the two answer different questions.

### Task 2: Guided modification

Traverse the slice using its indices.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
let values = [10, 20, 30, 40]
let slice = values[1...2]
var seen: [Int] = []
for index in slice.indices { seen.append(slice[index]) }
precondition(seen == [20, 30])
precondition(Array(slice.indices) == [1, 2])
```

**Observe:** Walking slice.indices visits indices 1 and 2 and reads 20 and 30.

slice.indices yields the slice's real positions, so every subscript is valid regardless of where the slice starts.

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

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
let values = [10, 20, 30, 40]
let slice = values[1...2]
precondition(!slice.indices.contains(0))
var total = 0
for offset in 0..<slice.count {
  total += slice[slice.index(slice.startIndex, offsetBy: offset)]
}
precondition(total == 50)
```

**Observe:** Index 0 is not in the slice, and offsetting from startIndex sums 20 + 30 = 50.

Looping slice[0..<count] would read index 0, which traps because the slice starts at 1; offsets must be converted to indices from startIndex.

### Task 5: Boundary evidence

Test an empty slice and a single-pass custom sequence.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
let empty = [1, 2, 3][3..<3]
precondition(empty.isEmpty && empty.startIndex == 3)
final class OneShot: Sequence, IteratorProtocol {
  var remaining: [Int]
  init(_ values: [Int]) { remaining = values }
  func next() -> Int? { remaining.isEmpty ? nil : remaining.removeFirst() }
}
let stream = OneShot([1, 2])
precondition(Array(stream) == [1, 2])
precondition(Array(stream).isEmpty)
```

**Observe:** The empty slice starts at 3 with no elements; the one-shot stream yields [1, 2] once and then nothing.

OneShot is its own iterator and consumes its state, so a second traversal sees an empty sequence; Sequence does not promise repeatable iteration.

### Task 6: Transfer and justify

Choose lazy or materialized processing for a large input and explain repeatability and memory costs.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** Example A slices `[10, 20, 30, 40]` with `1...2` and checks the slice's `startIndex` separately from its contents. Example B builds a lazy filter-then-map pipeline over `[1, 2, 3]` and materializes it with `Array`. The task 3 answer is a generic sum over any Sequence whose elements are numeric.

**Why it is correct.** An `ArraySlice` shares indices with its base array, so the slice starts at 1, contains 20 and 30, and maps to `[2, 3]`. The lazy pipeline does nothing until `Array(transformed)` iterates it; then 1 is filtered out and 2 and 3 become 20 and 30. In task 3 the same function sums Ints to 6 and Doubles to 4.0, and returns 0 for an empty sequence.

**A plausible wrong approach.** Looping `for i in 0..<slice.count { slice[i] }` treats the slice as if it started at 0. On this slice, `slice[0]` is outside its bounds and traps. Iterating `slice.indices` or using `for value in slice` is correct. Putting a side effect such as a counter inside the lazy `map` is another trap: it runs each time the pipeline is consumed.

**How to verify.** Print `slice.indices` in a scratch pad and confirm it is `1..<3`. Consume `transformed` twice with `Array` and confirm both results are `[20, 30]`, showing the pure pipeline is repeatable.

## Mechanism and diagnostic reasoning

Sequence promises iteration but not necessarily repeatability or efficient indexing. Collection adds reusable traversal with indices, and more specialized protocols add bidirectional or random access. Write an algorithm against the capability it needs rather than assuming every sequence behaves like an array.

Lazy transformations defer work until consumption. This can avoid intermediate storage, but it also delays side effects and errors. Keep transformation closures pure. A slice can retain original indices, so using zero-based offsets indiscriminately breaks otherwise generic code. Complexity belongs to the chosen collection and operation, not merely to its spelling.

`collection.indices` supplies valid positions. `lazy.map` creates deferred transformation. `Array(sequence)` materializes. reduce summarizes a sequence without requiring indexing.

Not every Sequence can be traversed repeatedly. Index movement may be linear. Side effects in lazy closures can run later or more often than a caller expects.

## Review before continuing

Run the reference and confirm it prints `swift-020: passed`, then rerun the guide's counterexample.
