# swift-018: Generics and relationships between types

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-017`

## Learning objectives

Write generic types and functions with the constraints their operations need. The central exercise is task 3: Create a generic immutable triple with a rotation operation.

## Purpose and mental model

Generics preserve type relationships across an algorithm or container. A generic pair stores two values of the same chosen type. The compiler rejects mixing unrelated types unless the API explicitly models that possibility. This is stronger and clearer than storing Any and casting later.

Constraints expose the capabilities an algorithm needs. Comparable permits ordering, while Equatable permits equality. Use the narrowest useful constraint and state behavior for ties and empty inputs. Generic abstraction is valuable when it removes duplicated mechanisms without erasing domain meaning.

## Vocabulary and concepts

**Generic parameter:** A type placeholder constrained at compile time.

**Constraint:** A required capability for a type argument.

**Type relationship:** A connection between input, stored and output types.

## How to run this lesson

Every call to `larger` lets the compiler infer `T`, so task 1 is done on paper before running anything. Task 4 adds a method call on an unconstrained `T`; the compiler rejects it with a message that the value has no such member, and that message belongs in your evidence table.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`func larger<T: Comparable>` introduces a constrained type parameter. The return type T preserves the input relationship. Generic structs use the same parameter syntax.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Reuse an ordering mechanism

The Comparable requirement makes ordering available without dynamic casts.

```swift
import Foundation

func larger<T: Comparable>(_ left: T, _ right: T) -> T { left >= right ? left : right }
struct Pair<T> {
  let first: T
  let second: T
  func swapped() -> Pair<T> { Pair(first: second, second: first) }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      precondition(larger(3, 8) == 8)
      precondition(larger("apple", "pear") == "pear")
    }
    print("swift-018: passed")
  }
}
```

**Observe:** One implementation preserves Int and String results.

**Trace.** In `larger(3, 8)`, both arguments are `Int`, so `T` is inferred as `Int`. The body compares 3 with 8, finds `3 >= 8` false and returns the right argument, 8. In `larger("apple", "pear")`, `T` is `String`, and the comparison is lexicographic: apple sorts before pear, so pear is returned. One function body serves both types because `Comparable` guarantees that `>=` exists. When the arguments are equal, the `>=` test is true and the left argument is returned, which matters only when equal values can be told apart.

### Example B: Preserve container element type

The relationship is encoded in the type rather than a runtime convention.

```swift
import Foundation

func larger<T: Comparable>(_ left: T, _ right: T) -> T { left >= right ? left : right }
struct Pair<T> {
  let first: T
  let second: T
  func swapped() -> Pair<T> { Pair(first: second, second: first) }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let pair = Pair(first: "left", second: "right")
      let swapped = pair.swapped()
      precondition(swapped.first == "right" && swapped.second == "left")
    }
    print("swift-018: passed")
  }
}
```

**Observe:** Swapping retains the same concrete element type.

**Trace.** `Pair(first: "left", second: "right")` infers `T` as `String`. `swapped()` constructs a new `Pair<T>` with the fields exchanged, so the result is a `Pair<String>` holding right and left. The original `pair` is a `let` and is not modified; the method returns a fresh value. Because the return type mentions the same `T`, the compiler knows `swapped.first` is a `String` without a cast, which is the relationship this example is about.

## Exercises

1. **Predict and explain.** Identify inferred generic types at every call.

2. **Guided modification.** Use larger with Double values and a tie.

3. **Independent construction.** Create a generic immutable triple with a rotation operation.

4. **Diagnose a defect.** Diagnose calling an unavailable method on an unconstrained T.

5. **Boundary evidence.** State tie behavior and test equal inputs.

6. **Transfer and justify.** Choose generic or existential abstraction for an API that must preserve concrete result type.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Any discards useful type information. Excessively broad constraints make reuse harder. A generic algorithm still needs domain-specific failure and ordering policies.

Tie behavior is the counterexample for task 5: `larger` returns the left argument for equal inputs, so a version written with `>` instead of `>=` returns the right one. With plain integers both answers print the same value. Use a type whose equal values remain distinguishable, such as a struct compared only by score but carrying a name, and check which name comes back.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Reuse an ordering mechanism) before changing anything, and confirm its observation: One implementation preserves Int and String results.
2. Compare Example B (Preserve container element type) with Example A and name the first line whose behavior differs. Its observation is: Swapping retains the same concrete element type.
3. Before opening the explanation, check your task 3 attempt (Create a generic immutable triple with a rotation operation) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

State what the constraint `T: Comparable` allows inside `larger` and what it forbids. Explain why `larger(3, 2.5)` infers `Double` for `T`, while passing an `Int` variable and a `Double` variable fails to compile. Describe one API that should return a generic `T` rather than `any Comparable`, and the reason.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The Generics chapter of the Swift book covers generic functions, generic types, type constraints and type inference at call sites.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-018: Generics and relationships between types.
Read courses/swift/guides/swift-018.md and courses/swift/lessons/swift-018.swift. Prerequisites: swift-017.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-018_solution.swift and
courses/swift/solutions/swift-018_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
