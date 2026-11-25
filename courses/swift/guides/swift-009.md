# swift-009: Arrays and copy-on-write value semantics

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-008`

## Learning objectives

Predict copy-on-write behavior of arrays and transform them without changing the source. The central exercise is task 3: Build a filtered array without changing the source.

## Purpose and mental model

Swift arrays are value types. Assigning an array produces a value that behaves independently when later mutated. The implementation can share backing storage until a write requires separation, a strategy called copy-on-write. The semantic promise is independent values, not a guarantee that every assignment immediately copies all bytes.

An array of class references still contains references as its element values. Copying the array separates its sequence structure but does not clone every referenced object. Keep that distinction in mind when building snapshots or undo history. Capacity is storage preparation and does not change the count of present elements.

## Vocabulary and concepts

**Value semantics:** Independent observable values after assignment and mutation.

**Copy-on-write:** Storage sharing until a mutation requires separation.

**Capacity:** Reserved storage distinct from logical count.

## How to run this lesson

Example B's capacity call has no visible effect, which is the point. Print `values.capacity` in a scratch pad if you are curious, but never write a check that depends on the exact number, because the standard library may reserve more than requested. Task 4 traps at runtime with an index out of range.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`[Int]` is an array type. append grows logical count; an index replaces an existing element. reserveCapacity prepares storage. ArraySlice may preserve original indices, so use its indices rather than assuming zero.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Mutate an independent array value

The language contract concerns observable behavior even if storage was initially shared.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let original = [1, 2]
      var changed = original
      changed.append(3)
      precondition(original == [1, 2])
      precondition(changed == [1, 2, 3])
    }
    print("swift-009: passed")
  }
}
```

**Observe:** Appending to the copy leaves the original unchanged.

**Trace.** `original` is the array `[1, 2]`. Assigning it to `changed` copies the value; the two may share one buffer at first, an optimization the language permits. The `append` on `changed` is a mutation, so `changed` obtains its own unique buffer before writing 3. Afterward `original` still reads `[1, 2]` and `changed` reads `[1, 2, 3]`, which is all the checks examine. Whether storage was ever shared cannot be observed by these checks; only the values are part of the contract.

### Example B: Do not confuse capacity and count

Capacity is a performance hint, not an index range.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      var values: [Int] = []
      values.reserveCapacity(20)
      precondition(values.count == 0)
      values.append(7)
      precondition(values.count == 1 && values[0] == 7)
    }
    print("swift-009: passed")
  }
}
```

**Observe:** Reserving twenty slots creates no logical elements.

**Trace.** `values` starts empty. `reserveCapacity(20)` requests storage for at least twenty elements but adds none, so `count` stays 0 and `values[0]` would still trap. `append(7)` adds the first logical element, and the count becomes 1, which makes index 0 valid and lets the check read 7. Capacity says how many elements can be added before a reallocation; count says which indices exist, and only positions in `0..<count` may be subscripted.

## Exercises

1. **Predict and explain.** Predict original and changed arrays after append.

2. **Guided modification.** Replace an element in the copy and retain the original.

3. **Independent construction.** Build a filtered array without changing the source.

4. **Diagnose a defect.** Diagnose indexing a reserved but still empty array.

5. **Boundary evidence.** Test an empty slice and a slice whose startIndex is not zero.

6. **Transfer and justify.** Explain what changes when array elements are mutable class instances.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Array value semantics do not recursively clone objects. Never assume ArraySlice starts at index zero. Repeated insertions at the front can create quadratic work.

For task 5, build `let slice = [10, 20, 30, 40][2...]`. Its `startIndex` is 2, not 0, so `slice[0]` traps even though the slice has two elements, and a loop over `0..<slice.count` reads the wrong positions. Write the traversal with `slice.indices` instead and check it on the empty slice `[1, 2][2...]`, where the loop must run zero times.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Mutate an independent array value) before changing anything, and confirm its observation: Appending to the copy leaves the original unchanged.
2. Compare Example B (Do not confuse capacity and count) with Example A and name the first line whose behavior differs. Its observation is: Reserving twenty slots creates no logical elements.
3. Before opening the explanation, check your task 3 attempt (Build a filtered array without changing the source) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain what copy-on-write guarantees and what it does not promise about memory. Predict the result of copying an array of class instances and changing a property through the copy. Explain why inserting at index 0 inside a loop over n elements can take time proportional to n squared.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The Collection Types chapter of the Swift book covers arrays and their mutating methods; Structures and Classes explains why arrays behave as values.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-009: Arrays and copy-on-write value semantics.
Read courses/swift/guides/swift-009.md and courses/swift/lessons/swift-009.swift. Prerequisites: swift-008.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-009_solution.swift and
courses/swift/solutions/swift-009_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
