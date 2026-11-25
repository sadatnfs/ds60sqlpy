# swift-011: Tuples, enums and associated values

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-010`

## Learning objectives

Model alternatives with enums and associated values handled by exhaustive switches. The central exercise is task 3: Model loading, ready and failed states with an enum.

## Purpose and mental model

A tuple groups a fixed set of values without introducing a new nominal type. It is useful for local multi-value results, but a named type is clearer when the same concept crosses several APIs. An enum represents one case from a finite set. Associated values attach data relevant only to that case.

Explicit cases prevent impossible combinations such as success=true with an error message and no result. A switch must handle the alternatives. This is a strong foundation for application state machines, parsing results and asynchronous loading state. Add a new case only when it represents a real domain distinction, then review every consumer.

## Vocabulary and concepts

**Tuple:** A fixed grouping of component values.

**Enum:** A type whose value is one declared case.

**Associated value:** Data carried by a particular enum case.

## How to run this lesson

Example B depends on the `Outcome` enum declared above `LessonMain`; copy only the body and the compiler reports that it cannot find `Outcome` in scope. For task 5, add a case and leave the switch unchanged on purpose, so you read the exhaustiveness error before fixing it.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`(count: Int, rejected: Int)` names tuple components. `enum Outcome { case value(Int); case invalid(String) }` binds case-specific payloads. `case .value(let count)` extracts only the matching payload.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Return two related counts

The grouping is useful locally without requiring an entire class hierarchy.

```swift
import Foundation

enum Outcome {
  case value(Int)
  case invalid(String)
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let summary = (accepted: 3, rejected: 2)
      precondition(summary.accepted + summary.rejected == 5)
    }
    print("swift-011: passed")
  }
}
```

**Observe:** Named tuple fields expose the accounting relationship.

**Trace.** `summary` is a tuple with two labeled `Int` components, accepted 3 and rejected 2. The labels let the check read `summary.accepted` and `summary.rejected` instead of `.0` and `.1`. The check adds them and compares the sum with 5, expressing the accounting rule that every item is accepted or rejected exactly once. Nothing about the tuple enforces that rule; it lives only in the check, which is a reason to promote the tuple to a struct once other code depends on it.

### Example B: Model distinct outcomes

The switch extracts data after establishing the state case.

```swift
import Foundation

enum Outcome {
  case value(Int)
  case invalid(String)
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let outcomes: [Outcome] = [.value(4), .invalid("negative")]
      let rendered = outcomes.map { outcome in
        switch outcome {
        case .value(let count): return "count:\(count)"
        case .invalid(let reason): return "error:\(reason)"
        }
      }
      precondition(rendered == ["count:4", "error:negative"])
    }
    print("swift-011: passed")
  }
}
```

**Observe:** Each outcome exposes only its own meaningful payload.

**Trace.** `outcomes` is an array of two values: `.value(4)` and `.invalid("negative")`. `map` calls its closure once per element. For the first, the switch matches `case .value(let count)`, binds 4 and returns count:4. For the second, it matches `.invalid(let reason)`, binds negative and returns error:negative. Each case reaches only its own payload, so there is no way to read a count from an invalid outcome. The switch has no default, so a new case would fail to compile here.

## Exercises

1. **Predict and explain.** Name the meaning of each tuple field.

2. **Guided modification.** Add a third accounting field only if its meaning is independent.

3. **Independent construction.** Model loading, ready and failed states with an enum.

4. **Diagnose a defect.** Diagnose several optional fields that permit contradictory state combinations.

5. **Boundary evidence.** Add a new enum case and inspect the compiler-reported consumers requiring updates.

6. **Transfer and justify.** Choose tuple or named enum/struct for a reusable public API and explain the tradeoff.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

An enum raw value and an associated value solve different problems. A catch-all default can conceal a newly added state. Avoid using tuples so large that their positional relationship becomes obscure.

Task 4's problem is easiest to see as a concrete contradictory value: a struct with `isLoading: Bool`, `data: [Int]?` and `error: String?` can be loading, loaded and failed at the same time, and it compiles. Build that value, then rewrite the type as an enum with loading, ready and failed cases and confirm the contradiction can no longer be written.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Return two related counts) before changing anything, and confirm its observation: Named tuple fields expose the accounting relationship.
2. Compare Example B (Model distinct outcomes) with Example A and name the first line whose behavior differs. Its observation is: Each outcome exposes only its own meaningful payload.
3. Before opening the explanation, check your task 3 attempt (Model loading, ready and failed states with an enum) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain when an enum needs raw values and when it needs associated values, with one example of each. Say what the compiler does when a switch over your enum lacks a case and has no default. Give one sign that a tuple returned from a function should become a named struct.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The Enumerations chapter of the Swift book covers associated values, raw values and matching enum cases; tuples are introduced in The Basics.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-011: Tuples, enums and associated values.
Read courses/swift/guides/swift-011.md and courses/swift/lessons/swift-011.swift. Prerequisites: swift-010.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-011_solution.swift and
courses/swift/solutions/swift-011_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
