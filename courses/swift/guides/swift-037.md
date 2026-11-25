# swift-037: Property wrappers and reusable access policy

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-036`

## Learning objectives

Write property wrappers that apply one reusable access or normalization policy. The central exercise is task 3: Create a wrapper with an explicit normalization policy for a local display field.

## Purpose and mental model

A property wrapper packages behavior around property storage and access. It can validate, normalize or project a reusable policy, but it should not hide surprising I/O or authorization. The wrappedValue is the property-facing interface; projectedValue can expose related information using dollar-prefixed access.

Wrapper behavior is part of the containing type's semantics. Decide whether invalid assignments are rejected, clamped or represented as an error, and make that choice visible to readers. A clamped value can be appropriate for a display control but inappropriate for financial input where silent correction hides an error.

## Vocabulary and concepts

**Property wrapper:** Reusable logic around a property access contract.

**Wrapped value:** The value exposed through the decorated property.

**Projection:** Additional wrapper-related information exposed separately.

## How to run this lesson

Both examples repeat the `Clamped` wrapper and the `Control` struct above `LessonMain`. The projection is read-only because `projectedValue` has only a getter: assigning to `control.$level` fails to compile with a message that `$level` is immutable. Task 4 asks for a written argument rather than code.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`@propertyWrapper` marks a wrapper type. wrappedValue supplies get/set behavior. `@Clamped var level` applies it. A projectedValue is read through `$level` when declared.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Apply a bounded display policy

The wrapper enforces a deliberate display range at every assignment.

```swift
import Foundation

@propertyWrapper struct Clamped {
  private var value: Int
  let range: ClosedRange<Int>
  init(wrappedValue: Int, _ range: ClosedRange<Int>) {
    self.range = range
    self.value = min(max(wrappedValue, range.lowerBound), range.upperBound)
  }
  var wrappedValue: Int {
    get { value }
    set { value = min(max(newValue, range.lowerBound), range.upperBound) }
  }
  var projectedValue: ClosedRange<Int> { range }
}
struct Control { @Clamped(0...10) var level = 0 }

@main
struct LessonMain {
  static func main() async throws {
    do {
      var control = Control()
      control.level = 12
      precondition(control.level == 10)
      control.level = -2
      precondition(control.level == 0)
    }
    print("swift-037: passed")
  }
}
```

**Observe:** Assignments are clamped into zero through ten.

**Trace.** `Control()` runs the wrapper's `init(wrappedValue: 0, 0...10)`, because the default value 0 becomes `wrappedValue` and `(0...10)` supplies the second argument. The initializer clamps 0 into range and stores it. Assigning 12 calls the `wrappedValue` setter, which computes the maximum of 12 and 0, then the minimum of that and 10, and stores 10. Assigning -2 gives the maximum of -2 and 0, which is 0, and the minimum with 10 leaves 0.

### Example B: Retain valid interior values

The projected information explains the policy without exposing mutable internal storage.

```swift
import Foundation

@propertyWrapper struct Clamped {
  private var value: Int
  let range: ClosedRange<Int>
  init(wrappedValue: Int, _ range: ClosedRange<Int>) {
    self.range = range
    self.value = min(max(wrappedValue, range.lowerBound), range.upperBound)
  }
  var wrappedValue: Int {
    get { value }
    set { value = min(max(newValue, range.lowerBound), range.upperBound) }
  }
  var projectedValue: ClosedRange<Int> { range }
}
struct Control { @Clamped(0...10) var level = 0 }

@main
struct LessonMain {
  static func main() async throws {
    do {
      var control = Control()
      control.level = 4
      precondition(control.level == 4)
      precondition(control.$level == 0...10)
    }
    print("swift-037: passed")
  }
}
```

**Observe:** A valid interior value is unchanged and the projection exposes the range.

**Trace.** Assigning 4 passes through the same setter: the maximum of 4 and 0 is 4 and the minimum of 4 and 10 is 4, so an interior value is stored unchanged. Reading `control.$level` calls the `projectedValue` getter, which returns the range 0...10. The projection lets callers inspect the policy, but it exposes neither the private stored `value` nor a way to change the range after construction.

## Exercises

1. **Predict and explain.** Trace initialization and both setter calls.

2. **Guided modification.** Change the allowed range and update boundary tests.

3. **Independent construction.** Create a wrapper with an explicit normalization policy for a local display field.

4. **Diagnose a defect.** Explain why silently clamping a payment amount would be misleading.

5. **Boundary evidence.** Test both endpoints and one value outside each.

6. **Transfer and justify.** Choose a wrapper or explicit validation method based on whether assignment can fail meaningfully.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A wrapper is not a substitute for validating external input. Hidden side effects make ordinary-looking assignment hard to reason about. Document projection and mutation semantics.

The initializer clamps too, which matters for the memberwise path: `Control(level: 15)` stores 10, not 15. A wrapper that clamped only in the setter would let that out-of-range value in. Task 5's set is -1, 0, 10 and 11. For task 4, a payment of 120 against a limit of 100 must be rejected with an error, since silently charging 100 hides the problem from the user.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Apply a bounded display policy) before changing anything, and confirm its observation: Assignments are clamped into zero through ten.
2. Compare Example B (Retain valid interior values) with Example A and name the first line whose behavior differs. Its observation is: A valid interior value is unchanged and the projection exposes the range.
3. Before opening the explanation, check your task 3 attempt (Create a wrapper with an explicit normalization policy for a local display field) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain which wrapper initializer runs for `@Clamped(0...10) var level = 0` and how each argument is supplied. State what `$level` returns and why it cannot be assigned. Give one field where silent clamping is a sensible display policy and one where it would mislead.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): Property wrappers, wrapped values, projected values and their initializers are covered in the second half of the Properties chapter.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-037: Property wrappers and reusable access policy.
Read courses/swift/guides/swift-037.md and courses/swift/lessons/swift-037.swift. Prerequisites: swift-036.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-037_solution.swift and
courses/swift/solutions/swift-037_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
