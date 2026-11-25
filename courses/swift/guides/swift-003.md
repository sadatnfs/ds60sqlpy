# swift-003: Numeric limits and intentional arithmetic

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-002`

## Learning objectives

Detect integer overflow with reporting arithmetic and use Decimal where exact decimal values matter. The central exercise is task 3: Write checked quantity addition that returns an explicit rejected outcome.

## Purpose and mental model

Integer values have bounded ranges. Ordinary overflowing integer arithmetic traps in Swift, while reporting-overflow operations return both a result and an overflow flag. Wrapping operators are explicit and useful for domains such as fixed-width bit arithmetic, but usually wrong for quantities or balances.

Floating-point values approximate many decimal fractions. Compare a result according to a numerical error contract rather than expecting every decimal identity to hold exactly. Decimal can represent base-ten financial quantities more naturally, but rounding and units still require a policy. A type choice does not replace domain reasoning.

## Vocabulary and concepts

**Overflow:** A result outside the representable range.

**Tolerance:** An allowed numerical error under a stated scale.

**Wrapping arithmetic:** Arithmetic modulo the fixed-width representation.

## How to run this lesson

Run Example A before task 1 so you can check your predicted flag and partial value. Task 2 uses `subtractingReportingOverflow`. Writing `UInt8(0) - 1` with the plain operator is a different experiment: the compiler can reject a constant overflow outright, and a computed one traps at runtime, so classify whichever failure you see.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`addingReportingOverflow` returns a tuple with partialValue and overflow. `&+` explicitly wraps. `abs(actual - expected) < tolerance` expresses a simple absolute error bound appropriate only to the stated scale.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Observe overflow without crashing

The flag is essential: the partial result alone cannot identify the intended mathematical sum.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let result = UInt8.max.addingReportingOverflow(1)
      precondition(result.overflow)
      precondition(result.partialValue == 0)
      precondition(UInt8(2).addingReportingOverflow(3).partialValue == 5)
    }
    print("swift-003: passed")
  }
}
```

**Observe:** 255 plus one reports overflow and a wrapped partial result of zero.

**Trace.** `UInt8.max` is 255, the largest value one unsigned byte holds. `addingReportingOverflow(1)` computes the true sum 256, keeps only the low eight bits and returns the tuple `(partialValue: 0, overflow: true)`. The first check reads the flag and the second reads the wrapped value. The last line is the control case: 2 plus 3 fits, so its partial value is 5 and its flag is false. Without the flag, a caller seeing 0 could not tell an overflowed 255 + 1 from a genuine 0 + 0.

### Example B: Use a numerical comparison policy

The force unwrap is limited to authored literal fixtures known to parse; external text needs conditional handling.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let actual = 0.1 + 0.2
      precondition(abs(actual - 0.3) < 1e-12)
      let exact = Decimal(string: "0.1")! + Decimal(string: "0.2")!
      precondition(exact == Decimal(string: "0.3")!)
    }
    print("swift-003: passed")
  }
}
```

**Observe:** The floating result meets the stated tolerance and the decimal fixture retains decimal intent.

**Trace.** `0.1 + 0.2` in `Double` produces 0.30000000000000004 because neither operand has an exact binary representation. The check therefore measures the distance from 0.3 and accepts anything closer than 1e-12, a bound chosen for values near 1. `Decimal(string:)` parses base-ten text and returns an optional; the force unwraps are safe only because these literals are authored here. Decimal addition of 0.1 and 0.2 gives exactly 0.3, so its equality check needs no tolerance.

## Exercises

1. **Predict and explain.** Predict the overflow flag and partial result.

2. **Guided modification.** Repeat the boundary with UInt8 zero minus one using the reporting operation.

3. **Independent construction.** Write checked quantity addition that returns an explicit rejected outcome.

4. **Diagnose a defect.** Diagnose ignoring the overflow flag.

5. **Boundary evidence.** Compare zero, normal and maximum-range inputs.

6. **Transfer and justify.** Choose a numeric representation and rounding policy for a price calculation.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A tolerance that hides a unit error is not a numerical policy. Avoid wrapping operators for business totals unless modulo behavior is intended. Never force-unwrap untrusted numeric text.

For checked quantity addition, the counterexample is the pair that sits exactly at the type's limit. With `Int8`, 100 + 27 is 127 and must be accepted, while 100 + 28 must produce your rejected outcome. An implementation that tests `sum > Int8.max` after a plain `+` never reaches its test, because the addition traps first. Keep 0 + 0 as the normal-range control.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Observe overflow without crashing) before changing anything, and confirm its observation: 255 plus one reports overflow and a wrapped partial result of zero.
2. Compare Example B (Use a numerical comparison policy) with Example A and name the first line whose behavior differs. Its observation is: The floating result meets the stated tolerance and the decimal fixture retains decimal intent.
3. Before opening the explanation, check your task 3 attempt (Write checked quantity addition that returns an explicit rejected outcome) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

In one sentence each, say what `addingReportingOverflow`, `&+` and plain `+` do when a result does not fit. Justify a tolerance of 1e-12 for sums near 1 and explain why the same bound fails for values near one billion. Name a case where `Decimal` is the better representation and the cost it carries.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The Advanced Operators chapter of the Swift book explains overflow operators, and the standard library reference documents `addingReportingOverflow(_:)` on `FixedWidthInteger`.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-003: Numeric limits and intentional arithmetic.
Read courses/swift/guides/swift-003.md and courses/swift/lessons/swift-003.swift. Prerequisites: swift-002.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-003_solution.swift and
courses/swift/solutions/swift-003_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
