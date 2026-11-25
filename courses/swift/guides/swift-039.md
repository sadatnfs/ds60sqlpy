# swift-039: App architecture: a portable domain core

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-038`

## Learning objectives

Separate a portable domain core from the Apple app and test it on its own. The central exercise is task 3: Build and test JourneyCore before opening the Apple app.

## Purpose and mental model

An app is a set of responsibilities with different lifetimes: domain rules, presentation state, views, persistence and external services. A portable domain core lets Linux tests establish business behavior independently of Apple UI rendering. The app adapter then translates user actions into core operations and renders their outcomes.

The JourneyCore package and JourneyApp fixture implement this separation with a small study planner. A lesson item has stable identity, title and completion state. The core rejects empty titles and duplicate identities. SwiftUI presents and edits those values on Apple platforms. Linux can compile and test the core, but cannot qualify view layout, accessibility or simulator behavior.

## Vocabulary and concepts

**Domain core:** Portable rules independent of UI frameworks.

**Reducer:** A function computing next state from current state and an action.

**Presentation state:** Values a view needs to explain current application behavior.

## How to run this lesson

The pad runs only the portable domain kernel; the SwiftUI app is a separate Apple project lab. Task 3 runs `swift test` in a copied JourneyCore package before you open JourneyApp, so a domain failure is found without Xcode. `PlannerItem` and `toggled` are declared above `LessonMain` in both examples.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).

Use [JourneyCore](../fixtures/JourneyCore/README.md) for the complete portable package and [JourneyApp](../fixtures/JourneyApp/README.md) for the real SwiftUI app files and Xcode workflow.

## Syntax anatomy and execution trace

A struct model conforms to Identifiable, Codable, Equatable and Sendable where appropriate. A pure reducer maps a state plus action to a new state. The app owns presentation and storage adapters.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Apply a domain action

A pure transition supports undo, testing and separate UI rendering.

```swift
import Foundation

struct PlannerItem: Equatable, Sendable {
  let id: String
  let title: String
  var completed: Bool
}
func toggled(_ item: PlannerItem) -> PlannerItem {
  var result = item
  result.completed.toggle()
  return result
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let original = PlannerItem(id: "one", title: "Read", completed: false)
      let changed = toggled(original)
      precondition(changed.completed && !original.completed)
    }
    print("swift-039: passed")
  }
}
```

**Observe:** The transformed item changes completion while retaining the original value.

**Trace.** `original` is a struct with completed set to false. `toggled` receives a copy, makes a mutable local `result` from it, flips completed to true and returns that new value. Because `PlannerItem` is a value type, the function never touches the caller's storage. The check confirms that `changed.completed` is true while `original.completed` is still false, so the old state remains available for undo or comparison.

### Example B: Keep identity stable during edits

Stable identity lets navigation, persistence and UI reconciliation refer to the same domain item.

```swift
import Foundation

struct PlannerItem: Equatable, Sendable {
  let id: String
  let title: String
  var completed: Bool
}
func toggled(_ item: PlannerItem) -> PlannerItem {
  var result = item
  result.completed.toggle()
  return result
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let original = PlannerItem(id: "one", title: "Read", completed: false)
      let changed = toggled(original)
      precondition(changed.id == original.id && changed.title == original.title)
    }
    print("swift-039: passed")
  }
}
```

**Observe:** Completion changes do not manufacture a new identity.

**Trace.** The same toggle runs, and the check now compares the fields that should not change. `id` and `title` are `let` constants in the struct, so no transition can alter them after creation; `toggled` copies them across unchanged. The new value carries the identity one, so a list, a navigation path or a saved file can still recognize it as the same item even though one property differs.

## Exercises

1. **Predict and explain.** Identify domain and presentation responsibilities.

2. **Guided modification.** Add a pure rename operation with nonempty-title validation.

3. **Independent construction.** Build and test JourneyCore before opening the Apple app.

4. **Diagnose a defect.** Diagnose placing file access directly inside a model property getter.

5. **Boundary evidence.** Test unknown identity and duplicate identity admission.

6. **Transfer and justify.** Draw the dependency direction among core, persistence adapter, view model and SwiftUI views.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A successful core test does not prove app rendering. Stable identity must survive edits and reloads. Keep domain validation outside UI-only button enablement.

Task 2's rename must reject an empty or all-whitespace title and leave the original untouched; the counterexample is a title of three spaces, which a plain `isEmpty` check accepts. For task 4, a model getter that reads a file runs whenever a view reads the property, so a missing file fails during rendering rather than during an explicit load step that can report the error.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Apply a domain action) before changing anything, and confirm its observation: The transformed item changes completion while retaining the original value.
2. Compare Example B (Keep identity stable during edits) with Example A and name the first line whose behavior differs. Its observation is: Completion changes do not manufacture a new identity.
3. Before opening the explanation, check your task 3 attempt (Build and test JourneyCore before opening the Apple app) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain why returning a new value supports undo more easily than mutating the original in place. Say which fields of `PlannerItem` can change and how the declaration enforces that. Draw the dependency direction among the core, persistence, view model and views, and state which layer may import SwiftUI.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): Value semantics for structs are explained in Structures and Classes; Apple's SwiftUI documentation covers the `Identifiable` protocol and list identity.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-039: App architecture: a portable domain core.
Read courses/swift/guides/swift-039.md and courses/swift/lessons/swift-039.swift. Prerequisites: swift-038.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-039_solution.swift and
courses/swift/solutions/swift-039_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
