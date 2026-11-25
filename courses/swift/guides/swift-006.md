# swift-006: Branches, switch and exhaustive reasoning

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: `swift-005`

## Learning objectives

Write exhaustive switch statements and guards that cover every case, including boundaries. The central exercise is task 3: Write a three-way classifier for negative, zero and positive quantities.

## Purpose and mental model

Control flow selects which operations execute. A branch should correspond to a domain distinction that can be explained before reading the code. Swift switch does not implicitly fall through to the next case, and the compiler requires coverage of possible inputs. This helps make state handling deliberate.

Range boundaries remain a source of mistakes. A closed range includes both ends; a half-open range excludes its upper end. Use fixtures exactly at transitions and outside the valid domain. A broad default can satisfy exhaustiveness while still hiding a new state, so prefer explicit enum cases when the domain is finite.

## Vocabulary and concepts

**Exhaustiveness:** Handling every possible input category.

**Closed range:** A range including both endpoints.

**Half-open range:** A range excluding its upper endpoint.

## How to run this lesson

Both examples declare their function inside `main`, so a copied function can be moved out to file scope without changing its behavior. Task 2 moves the pass boundary to 70, which changes two adjacent checks at once. Task 4 needs a deliberately wrong range, and that program still compiles, so only a boundary check will reveal it.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`if` requires a Bool. `switch` matches cases without implicit fallthrough. `0..<10` excludes ten; `0...10` includes it. A where clause narrows a matched case.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Classify thresholds

The ranges express the inclusive boundary and keep out-of-domain values separate.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      func classify(_ score: Int) -> String {
        switch score {
        case 0..<60: return "retry"
        case 60...100: return "pass"
        default: return "invalid"
        }
      }
      precondition(classify(59) == "retry")
      precondition(classify(60) == "pass" && classify(101) == "invalid")
    }
    print("swift-006: passed")
  }
}
```

**Observe:** 59 retries, 60 passes and 101 is invalid.

**Trace.** `classify(59)` reaches the `switch`, tests 59 against `0..<60`, which covers 0 through 59, and returns retry. `classify(60)` misses the first range because its half-open upper bound excludes 60, then matches `60...100`, whose closed bound includes both ends. `classify(101)` matches neither range and falls to `default`, which returns invalid. Swift tries cases from top to bottom, stops at the first match and never falls through implicitly, so each score returns exactly one label.

### Example B: Use a guard for a required value

The unwrapped binding is available after the guard because every failing path has returned.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      func describe(_ text: String?) -> String {
        guard let text, !text.isEmpty else { return "missing" }
        return "value:\(text)"
      }
      precondition(describe(nil) == "missing")
      precondition(describe("") == "missing" && describe("x") == "value:x")
    }
    print("swift-006: passed")
  }
}
```

**Observe:** The early exit excludes missing and empty values before the valid path.

**Trace.** `describe(nil)` reaches the guard, where optional binding fails and the else branch returns missing. `describe("")` binds successfully, but the second condition `!text.isEmpty` is false, so it also leaves through the else branch. `describe("x")` passes both conditions. After the guard, `text` is a non-optional `String` for the rest of the function, and the return builds value:x. The shorthand `guard let text` rebinds the same name, so the unwrapped value keeps its original name.

## Exercises

1. **Predict and explain.** Predict each threshold case before running.

2. **Guided modification.** Move the pass boundary to 70 and update adjacent tests.

3. **Independent construction.** Write a three-way classifier for negative, zero and positive quantities.

4. **Diagnose a defect.** Diagnose a closed range used where an exclusive upper bound was intended.

5. **Boundary evidence.** Test both ends of the valid domain and one value beyond each.

6. **Transfer and justify.** Replace a broad default in an enum switch with explicit cases and explain the maintenance benefit.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A default can hide future cases. Guard must actually exit on failure. Avoid treating every invalid value as the normal else category without a stated policy.

The counterexample for task 4's range defect is the boundary value itself. If the retry case is written as `0...60`, scores 0 to 59 still behave and only 60 changes, returning retry instead of pass. That is why task 5 asks for both ends of the valid domain plus one value beyond each: checking -1, 0, 59, 60, 100 and 101 pins every edge.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Classify thresholds) before changing anything, and confirm its observation: 59 retries, 60 passes and 101 is invalid.
2. Compare Example B (Use a guard for a required value) with Example A and name the first line whose behavior differs. Its observation is: The early exit excludes missing and empty values before the valid path.
3. Before opening the explanation, check your task 3 attempt (Write a three-way classifier for negative, zero and positive quantities) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Write a `switch` over an enum with three cases and no default, then add a fourth case and describe what the compiler reports. Explain `0..<10` versus `0...10` with the one value that distinguishes them. Say why the guard in Example B must return, throw or otherwise leave in its else branch.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The Control Flow chapter of the Swift book explains conditional statements, switch, interval matching, where clauses and early exit with guard.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-006: Branches, switch and exhaustive reasoning.
Read courses/swift/guides/swift-006.md and courses/swift/lessons/swift-006.swift. Prerequisites: swift-005.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-006_solution.swift and
courses/swift/solutions/swift-006_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
