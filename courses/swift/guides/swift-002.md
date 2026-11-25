# swift-002: Constants, variables and static types

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-001`

## Learning objectives

Use let and var deliberately and convert between numeric types explicitly. The central exercise is task 3: Compute a mean from an integer total and count using a deliberate conversion.

## Purpose and mental model

Swift distinguishes a binding that may change from one that may not. `let` prevents reassignment; `var` permits it. Prefer let until a state transition is part of the design. The compiler infers types from context, but inference does not make values dynamically typed. A variable initialized with an Int cannot later become a String.

Conversions are explicit between many numeric types. This makes information-changing boundaries visible. A value being representable in one type does not prove it is valid for a domain. Keep units in names and validation at input boundaries. Later chapters introduce reference types, where a constant reference can still point to a mutable object.

## Vocabulary and concepts

**Binding:** A name associated with a value or reference.

**Type inference:** Compiler deduction of a static type from context.

**Conversion:** An explicit change of representation.

## How to run this lesson

Task 2 changes an unnecessary `var` to `let`, which still compiles because nothing reassigns it. Make the same change to `total` in Example A and the compiler rejects the first `+=` instead, naming the constant. Run Example B before writing your own mean in task 3 so you have seen integer division truncate.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`let count: Int = 3` gives an explicit type. `var total = 0` infers Int. `Double(count)` converts a numeric value. Swift source normally does not need semicolons at line ends.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Reassign only mutable state

The code exposes which part is state and which part is a stable input.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let perBox = 4
      var total = 0
      total += perBox
      total += perBox
      precondition(total == 8 && perBox == 4)
    }
    print("swift-002: passed")
  }
}
```

**Observe:** The accumulator becomes 8 while the fixed amount remains 4.

**Trace.** `perBox` is a constant 4 and `total` starts at 0; both are inferred as `Int`. The first `+=` reads `total` (0), adds 4 and stores 4. The second reads 4 and stores 8. `perBox` never changes, and the compiler would reject any assignment to it because it is a `let`. The combined check confirms both facts at once: the accumulator moved to 8 and the input stayed 4. Change `var total` to `let total` and the program never runs, because the first `+=` becomes a compile error.

### Example B: Convert before division

Converting after integer division would preserve the already truncated result.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let whole = 7 / 2
      let fractional = Double(7) / Double(2)
      precondition(whole == 3)
      precondition(fractional == 3.5)
    }
    print("swift-002: passed")
  }
}
```

**Observe:** Integer division yields 3; floating division yields 3.5.

**Trace.** `7 / 2` has two `Int` operands, so Swift performs integer division and discards the remainder: `whole` is 3. `Double(7)` and `Double(2)` convert before dividing, so `fractional` is 3.5, a value binary floating point represents exactly. Compare the wrong order, `Double(7 / 2)`: the division happens first in `Int`, produces 3, and only then converts, giving 3.0. Both checks pass silently in the correct version; the second would stop the program under the late conversion.

## Exercises

1. **Predict and explain.** Identify the inferred type of every binding.

2. **Guided modification.** Replace an unnecessary var with let and explain why it still compiles.

3. **Independent construction.** Compute a mean from an integer total and count using a deliberate conversion.

4. **Diagnose a defect.** Diagnose conversion performed after integer division.

5. **Boundary evidence.** Test an exactly divisible and a non-divisible pair.

6. **Transfer and justify.** Choose units and types for a small measurement model.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Let protects the binding, not necessarily every object reachable from it. Avoid forced conversions at a boundary without validating range. A floating type is not automatically more appropriate for a count.

For the mean in task 3, the counterexample is any total that does not divide evenly by its count. A total of 10 over 4 items should give 2.5, but converting after dividing gives 2.0. An evenly divisible pair such as 12 over 4 gives 3.0 under both rules and hides the bug, so keep one pair of each kind in your checks, exactly as task 5 asks.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Reassign only mutable state) before changing anything, and confirm its observation: The accumulator becomes 8 while the fixed amount remains 4.
2. Compare Example B (Convert before division) with Example A and name the first line whose behavior differs. Its observation is: Integer division yields 3; floating division yields 3.5.
3. Before opening the explanation, check your task 3 attempt (Compute a mean from an integer total and count using a deliberate conversion) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

State the inferred type of `0`, `0.0` and `Double(count)` without running anything. Explain why `let` on an array binding prevents reassignment, then describe what `let` would and would not protect for a class instance. Finally, choose a type for a temperature reading and justify `Int` or `Double` for it.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): Read the sections on constants and variables, type safety, type inference and numeric type conversion in The Basics chapter of the Swift book.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-002: Constants, variables and static types.
Read courses/swift/guides/swift-002.md and courses/swift/lessons/swift-002.swift. Prerequisites: swift-001.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-002_solution.swift and
courses/swift/solutions/swift-002_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
