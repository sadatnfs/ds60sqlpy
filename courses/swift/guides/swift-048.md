# swift-048: Capstone: an offline-first study planner

## Level and prerequisites

Advanced, approximately 180 minutes. Prerequisites: `swift-047`

## Learning objectives

Build and test a complete offline-first study planner across the portable core and the Apple app. The central exercise is task 3: Build and test JourneyCore, then run the complete JourneyApp on a prepared Apple destination.

## Purpose and mental model

The final project connects a portable domain package, a SwiftUI application, stable navigation, editable state and versioned persistence. It remains offline by default so a learner can inspect every meaningful behavior without credentials or a remote service. The architecture has deliberate extension points for networking and additional data models.

A complete capstone includes evidence and limits. Explain which invariants the Linux kernel establishes, which package tests ran, which Apple destination rendered the UI and how saved-state recovery was checked. Keep an unsuccessful observation visible until it is resolved. Expertise grows through independent extensions and diagnosis, not through copying the final source or declaring every possible app scenario covered.

## Vocabulary and concepts

**Offline-first:** Core behavior works without a network dependency.

**Acceptance evidence:** Recorded observations establishing a declared requirement.

**Extension boundary:** A documented place for adding behavior without duplicating core rules.

## How to run this lesson

The pad runs the identity kernel; the capstone itself is the JourneyCore package and the JourneyApp project. Task 3 runs `swift test` first, then the app on an Apple destination you actually have. Task 4 asks you to break the app on purpose in a copy, record the symptom and then repair it.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).

Start from the actual [JourneyCore](../fixtures/JourneyCore/README.md) and [JourneyApp](../fixtures/JourneyApp/README.md) project files. The app project includes working list, detail editing, navigation, save/load and platform text-bridge code.

## Syntax anatomy and execution trace

A stable item identity connects domain actions, navigation and saved data. A reducer updates values; a MainActor presentation model owns view state; a persistence adapter encodes the versioned document. Each layer has its own test boundary.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Produce a stable completion summary

The report checks state and identity rather than only a formatted label.

```swift
import Foundation

struct CapstoneItem: Equatable, Sendable {
  let id: String
  var complete: Bool
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let items = [CapstoneItem(id: "a", complete: true), CapstoneItem(id: "b", complete: false)]
      precondition(items.filter(\.complete).count == 1)
      precondition(Set(items.map(\.id)).count == items.count)
    }
    print("swift-048: passed")
  }
}
```

**Observe:** One of two uniquely identified items is complete.

**Trace.** `items` holds a, which is complete, and b, which is not. `filter(\.complete)` keeps items whose complete property is true, leaving one. The second check maps items to their ids, builds a set of two and compares its count with the array's count of two; equal counts prove no identifier is repeated. Together the checks verify completion state and identity rather than a formatted label.

### Example B: Preserve identity across a value update

These are the core semantics needed by undo, navigation and persistence.

```swift
import Foundation

struct CapstoneItem: Equatable, Sendable {
  let id: String
  var complete: Bool
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let original = CapstoneItem(id: "a", complete: false)
      var changed = original
      changed.complete = true
      precondition(changed.id == original.id && !original.complete && changed.complete)
    }
    print("swift-048: passed")
  }
}
```

**Observe:** The update retains identity and the prior snapshot.

**Trace.** `original` is a with complete false. `var changed = original` copies the struct, and setting complete to true changes only the copy. The check confirms the copy kept id a, the original is still incomplete and the copy is complete. Undo can restore the old snapshot, navigation still finds a, and persistence writes the new value under the same id.

## Exercises

1. **Predict and explain.** Trace one user action from view through model to domain state.

2. **Guided modification.** Add a derived progress summary without duplicating stored completion counts.

3. **Independent construction.** Build and test JourneyCore, then run the complete JourneyApp on a prepared Apple destination.

4. **Diagnose a defect.** Introduce and repair a stale-binding, duplicate-identity or failed-save defect.

5. **Boundary evidence.** Verify empty state, long titles, duplicate IDs, malformed storage and save/reload.

6. **Transfer and justify.** Deliver a project README with architecture, actual platform evidence, accessibility observations, recovery policy and one independently implemented extension.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A passing portable reference does not qualify simulator interaction or app signing. Preserve user data when testing failure recovery. Keep scope and evidence honest when adding new frameworks or deployment targets.

For task 2, derive progress from the items rather than storing a counter; the counterexample toggles one item and checks the summary changes without any other update. For task 5, two items both with id a must be rejected on admission, since the uniqueness check above only detects them afterward. A malformed saved file must leave the source file in place and show an error.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Produce a stable completion summary) before changing anything, and confirm its observation: One of two uniquely identified items is complete.
2. Compare Example B (Preserve identity across a value update) with Example A and name the first line whose behavior differs. Its observation is: The update retains identity and the prior snapshot.
3. Before opening the explanation, check your task 3 attempt (Build and test JourneyCore, then run the complete JourneyApp on a prepared Apple destination) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Trace one tap on a completion toggle from the view, through the presentation model, to the domain update and the save. Explain why progress is derived rather than stored. List the platform evidence your README will report as performed and anything still unverified.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): Read the JourneyCore and JourneyApp READMEs in this course alongside Apple's SwiftUI and Xcode documentation and the Swift Package Manager guide.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-048: Capstone: an offline-first study planner.
Read courses/swift/guides/swift-048.md and courses/swift/lessons/swift-048.swift. Prerequisites: swift-047.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-048_solution.swift and
courses/swift/solutions/swift-048_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
