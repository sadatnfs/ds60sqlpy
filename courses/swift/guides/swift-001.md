# swift-001: A Swift source file and its explicit entrypoint

## Level and prerequisites

Beginner, approximately 90 minutes. Prerequisites: None. Begin with the source file and visible result.

## Learning objectives

Compile and run a Swift program with an explicit @main entry point and check a computed value with precondition. The central exercise is task 3: Compute the capacity of three shelves holding eight books each.

## Purpose and mental model

Swift is a compiled language used for portable tools and for applications built with platform frameworks. The language, its standard library and Apple user-interface frameworks are separate layers. A Linux Swift compiler can execute language and portable Foundation code. It does not provide SwiftUI or an iPhone simulator.

The classroom stages one main.swift file and compiles it in Swift 6 mode. An explicit @main type tells the compiler where execution begins. The wrapper uses an asynchronous throwing main so later lessons can keep the same shape. For now, statements execute in order. A compiler error means the program never reached main; a failed precondition means execution reached a violated assumption.

## Vocabulary and concepts

**Source:** The text submitted to a compiler.

**Entrypoint:** The operation called to begin execution.

**Precondition:** A required condition checked during execution.

## How to run this lesson

Paste Example A first. It is the smallest complete program in the track, and a missing brace or a statement placed outside `LessonMain` produces a compile diagnostic rather than a runtime failure. Tasks 1 to 3 fit in one pad; task 4 deliberately breaks the brace structure, so save a working copy before you try it.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

`@main` marks the entrypoint type. `struct LessonMain` names that type. `static func main() async throws` declares its entry method; async and throws are explained in later chapters. `let` binds a value that cannot be reassigned. `print` produces visible output.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Check before printing

The check establishes a specific observation before the program claims completion.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let greeting = "Hello, Swift"
      precondition(greeting.count == 12)
      print(greeting)
    }
    print("swift-001: passed")
  }
}
```

**Observe:** Hello, Swift appears before the lesson marker.

**Trace.** Before `main` runs, nothing exists. The first `let` binds `greeting` to a string of 12 Characters: five letters, the comma, the space and five more letters. The `precondition` evaluates `greeting.count == 12`, finds it true and does nothing visible. Only then does `print` write `Hello, Swift`. Change the literal to `Hello, Swift!` and the check sees 13, the process stops with a precondition failure, and the print never happens. That ordering is why the greeting appears only when its count has been verified.

### Example B: Compute an observable result

The second condition rejects the plausible mistake of adding dimensions instead of multiplying them.

```swift
import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let rows = 4
      let seatsPerRow = 6
      let seats = rows * seatsPerRow
      precondition(seats == 24)
      precondition(seats != rows + seatsPerRow)
    }
    print("swift-001: passed")
  }
}
```

**Observe:** The computed seat count is 24.

**Trace.** `rows` is 4 and `seatsPerRow` is 6, both inferred as `Int` from their literals. The multiplication produces 24 and binds it to `seats`. The first check confirms the product. The second compares 24 with `rows + seatsPerRow`, which is 10, so the inequality holds. It exists to document the plausible slip of typing `+` for `*`: with addition, `seats` would be 10 and the first check would already stop the program. Neither line prints anything; this example's only visible output would be the final marker.

## Exercises

1. **Predict and explain.** Predict the greeting count before execution.

2. **Guided modification.** Change the greeting and independently recount its characters.

3. **Independent construction.** Compute the capacity of three shelves holding eight books each.

4. **Diagnose a defect.** Remove a closing brace temporarily and classify the failure as compilation.

5. **Boundary evidence.** Check zero shelves and one shelf.

6. **Transfer and justify.** Model a three-level capacity calculation and explain every intermediate value.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Do not delete a failed precondition to reach the marker. Preserve the first compiler diagnostic before interpreting later errors. The entrypoint wrapper is required by this classroom compile contract.

The tempting wrong belief in this lesson is that a program which compiles has done its job. A one-character counterexample settles it: compute shelf capacity with `+` instead of `*` and the program still compiles and runs, and only a check on the expected 24 stops it. For task 5, zero shelves should give 0 and one shelf should give 8; the addition bug gives 8 and 9, so both boundaries expose it.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Check before printing) before changing anything, and confirm its observation: Hello, Swift appears before the lesson marker.
2. Compare Example B (Compute an observable result) with Example A and name the first line whose behavior differs. Its observation is: The computed seat count is 24.
3. Before opening the explanation, check your task 3 attempt (Compute the capacity of three shelves holding eight books each) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Without looking, write the lines that make a valid entry point for this classroom and say which one the compiler needs because of `-parse-as-library`. Explain why `let` suits every binding in Example B, what `precondition` does when its condition is false, and why the marker must be the last statement in `main`.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): The Swift book chapter The Basics covers constants, type inference and printing, and the Attributes reference page documents `@main`.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-001: A Swift source file and its explicit entrypoint.
Read courses/swift/guides/swift-001.md and courses/swift/lessons/swift-001.swift. Prerequisites: none.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-001_solution.swift and
courses/swift/solutions/swift-001_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
