# swift-021: Throwing functions and explicit result values

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-020`

## Learning objectives

Throw and handle typed errors and convert between throwing calls and Result values. The central exercise is task 3: Write a throwing validator for an inventory record.

## Purpose and mental model

Swift errors represent recoverable failure that a caller must acknowledge with try. A throwing function can return its normal type or throw an Error value. Catching belongs at a layer that can recover, translate or report meaningfully. A generic fallback can hide a failed operation as an ordinary empty result.

Result stores success or failure as a value, useful when an outcome must be retained or passed through another API. Optional absence and errors are different: a missing lookup may be expected, while malformed input carries a reason. Preserve those distinctions instead of force-trying external operations.

## Vocabulary and concepts

**Error:** A value describing recoverable failure.

**Throwing function:** A function that can exit through an error path.

**Result:** A stored success-or-failure value.

## How to run this lesson

Both examples share `QuantityError` and the throwing `parseQuantity` declared above `LessonMain`. A `try` call outside a `do` block inside the throwing `main` would propagate the error and end the program, so keep the rejected input inside `do` and `catch`. Task 2 adds a second error case, and every exhaustive catch must change with it.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`throws` declares failure capability. `try` acknowledges a throwing call. `do/catch` handles errors. Result<Success, Failure> stores an outcome, with Failure conforming to Error.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Validate before returning

Failure carries a domain category instead of masquerading as zero.

```swift
import Foundation

enum QuantityError: Error { case invalid }
func parseQuantity(_ text: String) throws -> Int {
  guard let value = Int(text), value >= 0 else { throw QuantityError.invalid }
  return value
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let parsed = try parseQuantity("3")
      precondition(parsed == 3)
      var rejected = false
      do { _ = try parseQuantity("-1") } catch QuantityError.invalid { rejected = true }
      precondition(rejected)
    }
    print("swift-021: passed")
  }
}
```

**Observe:** Three is accepted and a negative quantity is rejected.

**Trace.** `parseQuantity("3")` converts the text to 3, passes `value >= 0` and returns 3 normally, so `parsed` holds 3. The second call receives -1: `Int` parses it, but the guard's second condition fails, so the function throws `QuantityError.invalid` and never reaches its return. Control jumps to the matching `catch QuantityError.invalid` clause, which sets `rejected` to true. The check then proves the failure path actually ran, rather than assuming it did because no value appeared.

### Example B: Store an outcome for later inspection

Result separates when an operation executes from when its outcome is examined.

```swift
import Foundation

enum QuantityError: Error { case invalid }
func parseQuantity(_ text: String) throws -> Int {
  guard let value = Int(text), value >= 0 else { throw QuantityError.invalid }
  return value
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let outcome = Result { try parseQuantity("bad") }
      switch outcome {
      case .success: preconditionFailure("invalid input accepted")
      case .failure(let error): precondition(error is QuantityError)
      }
    }
    print("swift-021: passed")
  }
}
```

**Observe:** The stored outcome retains a QuantityError.

**Trace.** `Result { try parseQuantity("bad") }` uses the catching initializer: it runs the closure immediately, and because `Int("bad")` is nil the function throws, so the error is stored as `.failure` instead of propagating. The switch then inspects the stored outcome later. The success case would stop the program with a clear message. The failure case binds the stored error, typed `any Error`, and `is QuantityError` confirms the category survived storage.

## Exercises

1. **Predict and explain.** Trace the normal and throwing paths.

2. **Guided modification.** Distinguish malformed text from negative quantity with separate error cases.

3. **Independent construction.** Write a throwing validator for an inventory record.

4. **Diagnose a defect.** Diagnose try? used where discarding the error reason loses required evidence.

5. **Boundary evidence.** Test empty, zero and out-of-range input.

6. **Transfer and justify.** Choose Optional, throws or Result for three APIs and explain each semantic distinction.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Try! turns recoverable failure into a trap. Try? deliberately discards error detail, so use it only when absence is the intended contract. Do not catch assertion failures as ordinary input errors.

For task 4, `try? parseQuantity(text)` turns every failure into nil, so malformed text and a negative number become indistinguishable from each other. The counterexample pair is abc and -1: after task 2's split, they must report different error cases, and any code path using `try?` reports nil for both. Test empty text and a number beyond `Int.max` as well; both are malformed under this parser.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Validate before returning) before changing anything, and confirm its observation: Three is accepted and a negative quantity is rejected.
2. Compare Example B (Store an outcome for later inspection) with Example A and name the first line whose behavior differs. Its observation is: The stored outcome retains a QuantityError.
3. Before opening the explanation, check your task 3 attempt (Write a throwing validator for an inventory record) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Name the three places an error can go after a throwing call: handled in a `catch`, propagated with `try` in a throwing function, or converted with `try?`. Explain when storing a `Result` is better than handling the error immediately. Choose Optional, throws or Result for a cache lookup, a file read and a deferred network reply.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The Error Handling chapter of the Swift book covers throwing functions, do-catch and converting errors to optionals; the standard library reference documents `Result`.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-021: Throwing functions and explicit result values.
Read courses/swift/guides/swift-021.md and courses/swift/lessons/swift-021.swift. Prerequisites: swift-020.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-021_solution.swift and
courses/swift/solutions/swift-021_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
