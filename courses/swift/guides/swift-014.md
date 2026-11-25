# swift-014: Properties, observers and derived state

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-013`

## Learning objectives

Derive computed properties from one stored source of truth and use observers deliberately. The central exercise is task 3: Build a value model with one stored unit and a documented converted view.

## Purpose and mental model

A stored property retains data; a computed property derives a value from other state. Prefer deriving cheap dependent values instead of storing duplicates that can disagree. A property observer reacts to a stored-value change but should not become an invisible substitute for a clear domain operation.

Computed setters translate an external representation back into stored state. That translation may lose information, so document it. Access control can permit reading without external writing. Property wrappers later package reusable access behavior, but start by understanding the plain getter and setter contract.

## Vocabulary and concepts

**Stored property:** A field retaining state.

**Computed property:** A value derived on access.

**Observer:** Code invoked around a stored-property change.

## How to run this lesson

Both structs appear in both examples, so Example A compiles `Temperature` without using it and Example B does the same with `Rectangle`. That is harmless. Task 2 adds a perimeter as another computed property; if you write it as a stored `let` instead, task 4's stale-value bug appears as soon as the width changes.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`var area: Int { width * height }` computes a value. `get` and `set` define two-way access; newValue names the assigned value. didSet observes assignments after the new value is stored.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Derive instead of duplicating

One source of truth prevents stale duplicated state.

```swift
import Foundation

struct Rectangle {
  var width: Int
  var height: Int
  var area: Int { width * height }
}
struct Temperature {
  var celsius: Double
  var fahrenheit: Double {
    get { celsius * 9 / 5 + 32 }
    set { celsius = (newValue - 32) * 5 / 9 }
  }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      var rectangle = Rectangle(width: 3, height: 4)
      precondition(rectangle.area == 12)
      rectangle.width = 5
      precondition(rectangle.area == 20)
    }
    print("swift-014: passed")
  }
}
```

**Observe:** Area changes with width without a separately updated area field.

**Trace.** `rectangle` is created with width 3 and height 4. Reading `area` runs the getter, which multiplies the current stored values and returns 12; nothing is cached. Assigning 5 to `width` changes one stored property. The next read of `area` runs the getter again, now computing 5 times 4, and returns 20. Because `area` has no storage of its own, there is no moment at which it can disagree with the dimensions, which is the single source of truth idea in this lesson.

### Example B: Expose a conversion property

A computed property can expose a convenient representation while retaining one stored unit.

```swift
import Foundation

struct Rectangle {
  var width: Int
  var height: Int
  var area: Int { width * height }
}
struct Temperature {
  var celsius: Double
  var fahrenheit: Double {
    get { celsius * 9 / 5 + 32 }
    set { celsius = (newValue - 32) * 5 / 9 }
  }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      var temperature = Temperature(celsius: 0)
      precondition(temperature.fahrenheit == 32)
      temperature.fahrenheit = 212
      precondition(abs(temperature.celsius - 100) < 1e-9)
    }
    print("swift-014: passed")
  }
}
```

**Observe:** The getter and setter translate between temperature scales.

**Trace.** `temperature` stores `celsius` 0. Reading `fahrenheit` runs the getter: 0 times 9 divided by 5 plus 32 gives exactly 32.0. Assigning 212 runs the setter with `newValue` 212, which computes (212 minus 32) times 5 divided by 9 and stores 100 in `celsius`. Only Celsius is ever stored. The check compares against 100 with a small tolerance, because a setter that converts through floating-point division may land a rounding error away from the exact value for other inputs.

## Exercises

1. **Predict and explain.** Trace which properties are stored and which are derived.

2. **Guided modification.** Add a computed rectangle perimeter.

3. **Independent construction.** Build a value model with one stored unit and a documented converted view.

4. **Diagnose a defect.** Diagnose a separately stored area that is not updated after width changes.

5. **Boundary evidence.** Test zero and a non-integer conversion case.

6. **Transfer and justify.** Choose an explicit method instead of a setter for a state change with validation and failure.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Expensive computed properties can surprise callers who expect cheap access. Observers can hide cascading side effects. Avoid duplicating state unless there is a measured caching need and invalidation policy.

For task 4, add `var storedArea: Int` initialized to 12 alongside the computed `area`. Set `width` to 5: the computed value becomes 20 while the stored one stays 12, and a check comparing them exposes the bug immediately. For task 5, a Fahrenheit value such as 100 converts to 37.777..., so an exact equality check on the Celsius result would fail there.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Derive instead of duplicating) before changing anything, and confirm its observation: Area changes with width without a separately updated area field.
2. Compare Example B (Expose a conversion property) with Example A and name the first line whose behavior differs. Its observation is: The getter and setter translate between temperature scales.
3. Before opening the explanation, check your task 3 attempt (Build a value model with one stored unit and a documented converted view) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Point to each stored and each computed property in both structs and say how you can tell from the syntax. Explain why `rectangle` must be declared with `var` before `rectangle.width = 5` compiles. Give one state change that should be a throwing method rather than a property setter, and say what the setter could not report.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The Properties chapter of the Swift book covers stored properties, computed properties with getters and setters, read-only computed properties and property observers.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-014: Properties, observers and derived state.
Read courses/swift/guides/swift-014.md and courses/swift/lessons/swift-014.swift. Prerequisites: swift-013.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-014_solution.swift and
courses/swift/solutions/swift-014_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
