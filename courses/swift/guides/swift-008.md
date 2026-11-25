# swift-008: Functions, argument labels and value contracts

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-007`

## Learning objectives

Write functions with clear argument labels and choose between value parameters and inout. The central exercise is task 3: Write a pure function normalizing a quantity without mutating its caller.

## Purpose and mental model

A function groups a computation behind a contract. Swift distinguishes the argument label read at the call site from the parameter name used inside the body. Labels can make an API read as a clear operation rather than an unexplained list of positional values. Use the underscore label only when the surrounding context already makes the meaning clear.

Ordinary value arguments are passed with value semantics. An inout parameter explicitly grants temporary mutation of the caller value under Swift exclusivity rules. Prefer returned values for pure transformations and use inout when mutation is the actual interface. A function contract should state invalid-input behavior and whether any state changes before failure.

## Vocabulary and concepts

**Argument label:** The name used at the call site.

**Parameter:** The local name of an input inside a function.

**Inout:** Explicit temporary mutable access to a caller value.

## How to run this lesson

Example B compiles only with the ampersand at the call site. Remove it in task 4 and the compiler reports that passing a value to an inout parameter requires an explicit `&`; copy that diagnostic into your notes. Tasks 2 and 3 change function signatures, so update every call site before running.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`func area(width: Int, height: Int) -> Int` exposes labels. `_ value` removes the external label. `inout` in a declaration pairs with `&` at the call site. `return` supplies the result and exits.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Name the dimensions

Readable call sites reduce accidental parameter swaps and reveal the function purpose.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      func area(width: Int, height: Int) -> Int { width * height }
      precondition(area(width: 3, height: 4) == 12)
      precondition(area(width: 0, height: 4) == 0)
    }
    print("swift-008: passed")
  }
}
```

**Observe:** Labels show which dimension each argument supplies.

**Trace.** `area(width:height:)` has two labeled parameters and a single-expression body, so the product is returned implicitly. The call `area(width: 3, height: 4)` binds 3 to `width` and 4 to `height` and returns 12. The second call passes 0 for the width; the product is 0, and the check records that the function currently accepts a zero dimension. Writing the labels in the other order, `area(height: 4, width: 3)`, is a compile error, because labeled arguments must appear in declaration order.

### Example B: Make mutation explicit

The ampersand makes the mutation boundary visible instead of hiding it behind a normal-looking value call.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      func increment(_ value: inout Int) { value += 1 }
      var count = 4
      increment(&count)
      precondition(count == 5)
    }
    print("swift-008: passed")
  }
}
```

**Observe:** The caller explicitly grants mutation and observes 5.

**Trace.** `count` is a `var` holding 4. The call `increment(&count)` gives the function access to that variable's storage for the duration of the call: inside, `value += 1` reads 4 and writes 5 back. When the function returns, `count` holds 5, which the check confirms. The `&` is required so that mutation is visible where it happens, and the argument must be a variable. Passing a `let` constant or a literal is a compile error, because neither has storage the function could write.

## Exercises

1. **Predict and explain.** Explain each argument label and local parameter name.

2. **Guided modification.** Add a depth label for a volume function.

3. **Independent construction.** Write a pure function normalizing a quantity without mutating its caller.

4. **Diagnose a defect.** Diagnose an inout call missing the ampersand and explain the compiler rule.

5. **Boundary evidence.** Test zero and negative dimensions under a documented validation policy.

6. **Transfer and justify.** Choose return values or inout for an API and justify who owns state changes.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Labels are part of API usability. Inout access cannot overlap conflicting access to the same storage. Do not use mutation merely to avoid returning a small value.

For task 3, an inout normalizer works too, so the useful counterexample is about the caller. A pure function can normalize `let original = -5` and leave the constant untouched, while an inout version refuses a `let` and forces the caller to make it mutable. Then test 0 and a negative dimension under the validation policy you documented for task 5.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Name the dimensions) before changing anything, and confirm its observation: Labels show which dimension each argument supplies.
2. Compare Example B (Make mutation explicit) with Example A and name the first line whose behavior differs. Its observation is: The caller explicitly grants mutation and observes 5.
3. Before opening the explanation, check your task 3 attempt (Write a pure function normalizing a quantity without mutating its caller) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Using `func move(from start: Int)`, explain the difference between an argument label and a parameter name. Say when `_` is a reasonable label. Explain why `swap(&a, &a)` fails to compile with the message that inout arguments are not allowed to alias, and what Swift's exclusive-access rule protects.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The Functions chapter of the Swift book covers argument labels, omitted labels and in-out parameters; Memory Safety explains conflicting access.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-008: Functions, argument labels and value contracts.
Read courses/swift/guides/swift-008.md and courses/swift/lessons/swift-008.swift. Prerequisites: swift-007.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-008_solution.swift and
courses/swift/solutions/swift-008_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
