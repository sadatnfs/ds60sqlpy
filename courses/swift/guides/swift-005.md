# swift-005: Optionals and honest absence

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-004`

## Learning objectives

Represent absence with optionals and unwrap them safely without inventing sentinel values. The central exercise is task 3: Write a parser accepting only present nonnegative integers.

## Purpose and mental model

An optional represents either a wrapped value or no value. This makes absence part of the type rather than an undocumented sentinel. Int zero can be a real measurement, so it should not also mean missing. Optional binding introduces a nonoptional value only inside the branch where presence has been established.

A force unwrap asserts that absence is impossible and traps if that assertion is wrong. It is suitable for tightly controlled fixture literals but is usually a poor external-input policy. Prefer if let for branching and guard let for an early-exit precondition. A fallback with ?? is valid only when the domain really assigns that replacement meaning.

## Vocabulary and concepts

**Optional:** A value that may be present or absent.

**Unwrapping:** Accessing a wrapped value after establishing presence.

**Nil:** The absent optional case.

## How to run this lesson

Both examples compile only because every optional is unwrapped or compared before use; delete the `if let` and the compiler reports the missing unwrap. Task 4 fails at runtime instead: force-unwrapping the result of parsing forty-two stops the process with an unexpectedly-found-nil error, so keep that experiment in a separate pad.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`Int?` abbreviates Optional<Int>. `if let value = optional` unwraps on the present branch. `guard let` requires an early exit on failure. `??` selects a fallback only when the optional is nil.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Preserve zero as a value

The branch proves presence before the wrapped integer is used.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let measured: Int? = 0
      let missing: Int? = nil
      precondition(measured != nil && missing == nil)
      if let value = measured {
        precondition(value == 0)
      } else {
        preconditionFailure("present zero")
      }
    }
    print("swift-005: passed")
  }
}
```

**Observe:** A present zero remains distinct from nil.

**Trace.** `measured` holds `Optional(0)` and `missing` holds nil; both have type `Int?`. The first check proves they are different states, even though a careless reading treats zero as nothing. The `if let` examines `measured`, finds a wrapped value, binds it to `value` of plain type `Int` and enters the first branch, where the check confirms 0. The else branch calls `preconditionFailure`, so a regression that turned a present zero into nil would stop the program with the message present zero.

### Example B: Parse with an absence policy

The fallback is an explicit display sentinel in this fixture, not a valid quantity.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let valid = Int("42")
      let invalid = Int("forty-two")
      precondition(valid == 42 && invalid == nil)
      precondition((invalid ?? -1) == -1)
    }
    print("swift-005: passed")
  }
}
```

**Observe:** Parsing produces an optional and malformed text is absent.

**Trace.** `Int("42")` succeeds and returns `Optional(42)`. Parsing forty-two fails, and the initializer returns nil instead of throwing or trapping. The first check compares each optional directly with a value, which Swift allows because `Optional` is equatable when its wrapped type is. The `??` operator then examines `invalid`, finds nil and substitutes -1. That -1 is only a display marker in this fixture; adding it to a real quantity total would quietly corrupt the sum, which is why the lesson calls it a sentinel.

## Exercises

1. **Predict and explain.** Explain the difference between nil and a wrapped zero.

2. **Guided modification.** Replace the display sentinel with an unknown label.

3. **Independent construction.** Write a parser accepting only present nonnegative integers.

4. **Diagnose a defect.** Diagnose force-unwrapping malformed external text.

5. **Boundary evidence.** Test empty, zero, negative and out-of-range input.

6. **Transfer and justify.** Model an optional measurement whose absence must survive serialization and reporting.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Optional chaining preserves absence; it does not validate the remaining value. A default chosen too early can erase meaningful missingness. Never silence absence merely to satisfy a compiler diagnostic.

A parser for present nonnegative integers goes wrong subtly if it uses `Int(text) ?? 0`: malformed text and the input 0 both produce 0, and a caller can no longer tell them apart. The counterexample pair is therefore the text 0 and the text abc. Your version must return 0 for the first and nil for the second, and nil for -3, for empty text and for a value beyond `Int.max`.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Preserve zero as a value) before changing anything, and confirm its observation: A present zero remains distinct from nil.
2. Compare Example B (Parse with an absence policy) with Example A and name the first line whose behavior differs. Its observation is: Parsing produces an optional and malformed text is absent.
3. Before opening the explanation, check your task 3 attempt (Write a parser accepting only present nonnegative integers) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain the difference between `Optional(0)` and nil to someone who expects them to be equal. Say when `guard let` fits better than `if let`, and what the compiler requires of a guard's else branch. Describe one report where a missing measurement must stay visibly missing rather than become zero.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The Swift book covers optionals and optional binding in The Basics, nil-coalescing in Basic Operators, and optional chaining in its own chapter.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-005: Optionals and honest absence.
Read courses/swift/guides/swift-005.md and courses/swift/lessons/swift-005.swift. Prerequisites: swift-004.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-005_solution.swift and
courses/swift/solutions/swift-005_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
