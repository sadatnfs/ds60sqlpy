# swift-015: Closures, captures and transformation pipelines

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-014`

## Learning objectives

Write closures, control what they capture and compose transformation pipelines. The central exercise is task 3: Write a function accepting a transformation closure.

## Purpose and mental model

A closure is executable behavior that can be passed as a value. It can capture surrounding variables, which lets it remember context but can also create surprising mutation or lifetime relationships. Swift capture lists can copy a value at closure creation or weaken a reference, depending on the declared policy.

Map transforms each element while filter selects elements. These operations express intent when the closure remains small and clear. Avoid compressing a complex domain algorithm into a chain whose intermediate states nobody can inspect. Name important transformations and preserve a traceable failure boundary.

## Vocabulary and concepts

**Closure:** Callable behavior that may carry surrounding context.

**Capture list:** An explicit policy for captured values or references.

**Higher-order function:** A function that accepts or returns functions.

## How to run this lesson

Example B's closure uses an explicit capture list, so its result does not depend on later changes to `factor`. For task 4, delete `[factor]` and run again before predicting: the check on 6 fails at runtime because the closure now reads the variable when it is called. Task 2 chains `filter` before `map` on the same array.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`{ value in value * 2 }` is a closure. `$0` abbreviates its first argument. A capture list such as `[factor]` captures the current value. Function types use `(Input) -> Output`.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Transform a sequence

The transformation is pure and its element-to-element relationship is visible.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let values = [1, 2, 3]
      let doubled = values.map { value in value * 2 }
      precondition(doubled == [2, 4, 6])
      precondition(values == [1, 2, 3])
    }
    print("swift-015: passed")
  }
}
```

**Observe:** Map creates transformed values while retaining the original array.

**Trace.** `values` is `[1, 2, 3]`. `map` creates a new array by calling the closure once per element in order: 1 gives 2, 2 gives 4 and 3 gives 6. The closure only reads its parameter and returns a value, so the source array is untouched, which the second check confirms. `map` always returns exactly as many elements as it receives; a step that can drop elements needs `filter` or `compactMap` instead.

### Example B: Freeze a captured value deliberately

This differs from a closure observing a mutable captured variable later.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      var factor = 2
      let scale = { [factor] (value: Int) in value * factor }
      factor = 5
      precondition(scale(3) == 6 && factor == 5)
    }
    print("swift-015: passed")
  }
}
```

**Observe:** The explicit capture list retains factor 2 for the closure.

**Trace.** `factor` starts at 2. The capture list `[factor]` copies the current value, 2, into the closure when the closure expression is evaluated. Reassigning `factor` to 5 afterward changes the variable but not that copy. Calling `scale(3)` multiplies 3 by the captured 2 and returns 6, while `factor` itself now reads 5. Without the capture list, the closure would capture the variable and read 5 at call time, returning 15 instead.

## Exercises

1. **Predict and explain.** Predict the mapped result and unchanged source.

2. **Guided modification.** Filter even numbers before mapping.

3. **Independent construction.** Write a function accepting a transformation closure.

4. **Diagnose a defect.** Diagnose a closure whose captured mutable state changes before later execution.

5. **Boundary evidence.** Test empty arrays and a closure that returns an optional.

6. **Transfer and justify.** Choose a named function or closure for a reusable domain transformation and explain readability and capture policy.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

An escaping closure can outlive its creating scope. Capturing self strongly can create a retain cycle, covered in ARC. A short expression is not automatically clearer than a named intermediate.

The regression for task 4 is a pair of runs that differ only in whether `[factor]` is present. Keep both versions in your notes with the observed 6 and 15. For task 5, an empty array must map to an empty array without calling the closure, and a closure returning `Int?` used with plain `map` produces `[Int?]`, whereas `compactMap` drops the nil results.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Transform a sequence) before changing anything, and confirm its observation: Map creates transformed values while retaining the original array.
2. Compare Example B (Freeze a captured value deliberately) with Example A and name the first line whose behavior differs. Its observation is: The explicit capture list retains factor 2 for the closure.
3. Before opening the explanation, check your task 3 attempt (Write a function accepting a transformation closure) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain the difference between capturing a variable and capturing its value through a capture list. Rewrite Example A's closure in shorthand form with `$0`. Say when a named function is clearer than an inline closure for a reusable domain transformation, and what a reader gains from the name.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The Closures chapter of the Swift book covers closure expression syntax, shorthand argument names, trailing closures and capturing values.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-015: Closures, captures and transformation pipelines.
Read courses/swift/guides/swift-015.md and courses/swift/lessons/swift-015.swift. Prerequisites: swift-014.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-015_solution.swift and
courses/swift/solutions/swift-015_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
