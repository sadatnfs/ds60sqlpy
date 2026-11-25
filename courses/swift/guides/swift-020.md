# swift-020: Collection protocols, laziness and algorithm costs

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-019`

## Learning objectives

Work with collection protocols, slices and lazy sequences and reason about their cost. The central exercise is task 3: Write a generic sum over Sequence where the element type is suitable.

## Purpose and mental model

Sequence promises iteration but not necessarily repeatability or efficient indexing. Collection adds reusable traversal with indices, and more specialized protocols add bidirectional or random access. Write an algorithm against the capability it needs rather than assuming every sequence behaves like an array.

Lazy transformations defer work until consumption. This can avoid intermediate storage, but it also delays side effects and errors. Keep transformation closures pure. A slice can retain original indices, so using zero-based offsets indiscriminately breaks otherwise generic code. Complexity belongs to the chosen collection and operation, not merely to its spelling.

## Vocabulary and concepts

**Sequence:** A source that can be iterated.

**Collection:** A sequence with reusable traversal and indices.

**Materialization:** Creating stored elements from a sequence.

## How to run this lesson

Predict `count` and `startIndex` of the slice separately before running Example A; task 1 asks for both. Task 4 indexes the slice from 0, which compiles and then traps at runtime with an index out of range, so run it in a scratch pad. Task 3 needs a constraint such as `AdditiveArithmetic` on the element type.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`collection.indices` supplies valid positions. `lazy.map` creates deferred transformation. `Array(sequence)` materializes. reduce summarizes a sequence without requiring indexing.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Use slice indices honestly

Element count and index origin are different properties.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let values = [10, 20, 30, 40]
      let slice = values[1...2]
      precondition(slice.startIndex == 1)
      precondition(slice.map { $0 / 10 } == [2, 3])
    }
    print("swift-020: passed")
  }
}
```

**Observe:** The slice starts at index 1 while traversal still produces two elements.

**Trace.** `values` holds four elements at indices 0 to 3. `values[1...2]` creates an `ArraySlice` that shares the original storage and keeps the original positions: its `startIndex` is 1, its `endIndex` is 3 and its count is 2. `map` traverses by position from start to end, reading 20 and 30 and dividing each by 10, which yields `[2, 3]`. The traversal never touches indices 0 or 3, and it would be wrong to assume `slice[0]` refers to 20.

### Example B: Materialize a lazy transformation

Pure transformations keep delayed execution understandable and reproducible.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let transformed = [1, 2, 3].lazy.filter { $0 > 1 }.map { $0 * 10 }
      precondition(Array(transformed) == [20, 30])
      precondition([Int]().reduce(0, +) == 0)
    }
    print("swift-020: passed")
  }
}
```

**Observe:** The lazy recipe produces 20 and 30 when consumed.

**Trace.** `[1, 2, 3].lazy` wraps the array so that `filter` and `map` build a recipe instead of new arrays. Nothing runs until `Array(transformed)` iterates the recipe. Then each element flows through both steps: 1 fails the filter, 2 passes and becomes 20, 3 passes and becomes 30. Iterating `transformed` again would run both closures again, so they must be pure. The second check is an unrelated reminder that reducing an empty array returns its initial value.

## Exercises

1. **Predict and explain.** Predict slice count and startIndex separately.

2. **Guided modification.** Traverse the slice using its indices.

3. **Independent construction.** Write a generic sum over Sequence where the element type is suitable.

4. **Diagnose a defect.** Diagnose indexing a slice from zero to count minus one.

5. **Boundary evidence.** Test an empty slice and a single-pass custom sequence.

6. **Transfer and justify.** Choose lazy or materialized processing for a large input and explain repeatability and memory costs.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Not every Sequence can be traversed repeatedly. Index movement may be linear. Side effects in lazy closures can run later or more often than a caller expects.

Task 4's loop `for i in 0..<slice.count { slice[i] }` traps immediately on `values[1...2]`, because index 0 is outside the slice. On a slice that happens to start at 0 the same loop works, but only by coincidence, so the safe rewrite uses `slice.indices`. For task 5, an empty slice such as `values[2..<2]` must run zero iterations.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Use slice indices honestly) before changing anything, and confirm its observation: The slice starts at index 1 while traversal still produces two elements.
2. Compare Example B (Materialize a lazy transformation) with Example A and name the first line whose behavior differs. Its observation is: The lazy recipe produces 20 and 30 when consumed.
3. Before opening the explanation, check your task 3 attempt (Write a generic sum over Sequence where the element type is suitable) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain why an `ArraySlice` keeps its parent's indices instead of renumbering from 0. Say what work happens when a lazy chain is created and what happens when it is iterated twice. Choose between lazy and materialized processing for a one-pass import of a million rows and justify the memory and repeatability tradeoff.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The standard library reference documents `ArraySlice`, the `Collection` and `Sequence` protocols, and `LazySequence`; Collection Types in the Swift book covers basic iteration.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-020: Collection protocols, laziness and algorithm costs.
Read courses/swift/guides/swift-020.md and courses/swift/lessons/swift-020.swift. Prerequisites: swift-019.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-020_solution.swift and
courses/swift/solutions/swift-020_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
