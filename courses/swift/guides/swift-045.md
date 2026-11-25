# swift-045: UIKit and AppKit integration boundaries

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-044`

## Learning objectives

Wrap UIKit and AppKit views at clear integration boundaries. The central exercise is task 3: Inspect and build SelectableText.swift in the Apple project.

## Purpose and mental model

SwiftUI can host platform-native views through representable adapters. UIKit serves iOS-family interfaces, while AppKit serves macOS. These frameworks do not exist inside the Linux worker. The adapter translates value-driven SwiftUI updates into an imperative view lifecycle and translates callbacks back into application actions.

A coordinator commonly owns delegate behavior. It must avoid feedback loops where a programmatic update triggers the same callback as a user edit and repeatedly writes state. Keep identity and lifetime explicit, and release delegates or observers when the view is dismantled. The fixture includes actual conditional UIKit and AppKit bridge source for a selectable text view.

## Vocabulary and concepts

**Representable adapter:** A SwiftUI bridge to an imperative platform view.

**Coordinator:** An object owning delegate or callback integration.

**Feedback loop:** An update triggering a callback that repeats the same update indefinitely.

## How to run this lesson

The pad runs only the comparison kernel. `SelectableText.swift` imports UIKit or AppKit behind `canImport`, so task 3 compiles in the Apple project, not on Linux. Count assignments in your own tests as task 2 does, since redundant updates do not show up as wrong output.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).

The complete [JourneyApp fixture](../fixtures/JourneyApp/README.md) contains `SelectableText.swift` with real UIKit and AppKit representable implementations.

## Syntax anatomy and execution trace

UIViewRepresentable uses makeUIView and updateUIView. NSViewRepresentable has corresponding AppKit methods. A Coordinator bridges delegate callbacks. Compile-time canImport guards select the appropriate platform source.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Avoid redundant imperative updates

A value comparison can prevent unnecessary callback or layout churn at the bridge boundary.

```swift
import Foundation

struct TextBridgeState {
  var text: String
  var assignments: Int
  mutating func update(_ incoming: String) {
    guard text != incoming else { return }
    text = incoming
    assignments += 1
  }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      var bridge = TextBridgeState(text: "old", assignments: 0)
      bridge.update("new")
      bridge.update("new")
      precondition(bridge.text == "new" && bridge.assignments == 1)
    }
    print("swift-045: passed")
  }
}
```

**Observe:** The same value is not assigned twice.

**Trace.** `bridge` starts with text old and zero assignments. The first `update("new")` finds the text differs, stores new and increments the count to 1. The second `update("new")` finds the text already equal and returns at the guard. The check confirms text new and one assignment. In a real `updateUIView`, skipping the equal case avoids resetting the selection or cursor on every SwiftUI update.

### Example B: Retain user changes as actions

The actual platform delegate must route its edit through the same single-source policy.

```swift
import Foundation

struct TextBridgeState {
  var text: String
  var assignments: Int
  mutating func update(_ incoming: String) {
    guard text != incoming else { return }
    text = incoming
    assignments += 1
  }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      var bridge = TextBridgeState(text: "start", assignments: 0)
      bridge.update("edited")
      precondition(bridge.text == "edited")
      precondition(bridge.assignments == 1)
    }
    print("swift-045: passed")
  }
}
```

**Observe:** The portable kernel exposes a deliberate state transition.

**Trace.** This run begins at start with zero assignments. One update with edited changes the text and counts one assignment, and both checks confirm it. In the platform view, the user's typing arrives through a delegate in the Coordinator, which writes to the binding; SwiftUI then calls the update method, and the guard sees the same text and does nothing. Both directions pass through one comparison.

## Exercises

1. **Predict and explain.** Identify the value-driven and imperative sides of the bridge.

2. **Guided modification.** Add a no-op case and verify no extra assignment.

3. **Independent construction.** Inspect and build SelectableText.swift in the Apple project.

4. **Diagnose a defect.** Diagnose an update callback that writes the same binding recursively.

5. **Boundary evidence.** Test empty text, large text and repeated updates in the platform view.

6. **Transfer and justify.** Document coordinator ownership, delegate cleanup and platform-specific API availability.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

A canImport branch is not evidence that both platforms were tested. UIKit and AppKit lifecycles differ. Avoid retaining transient SwiftUI view values as permanent controller state.

Task 4's loop comes from an update method that writes back to the binding unconditionally. The write triggers another update, which writes again, and the view never settles. The counterexample is a repeated-update test that expects the assignment count to stay at 1 after the second identical value. For task 5, empty text must still count as one change from a nonempty value.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Avoid redundant imperative updates) before changing anything, and confirm its observation: The same value is not assigned twice.
2. Compare Example B (Retain user changes as actions) with Example A and name the first line whose behavior differs. Its observation is: The portable kernel exposes a deliberate state transition.
3. Before opening the explanation, check your task 3 attempt (Inspect and build SelectableText.swift in the Apple project) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Name the two methods of `UIViewRepresentable` and say which one may run many times. Explain what the Coordinator owns and why delegate callbacks route through it. Describe how `canImport` lets one source file supply UIKit and AppKit implementations. Starting from start, predict the assignment count after updates with a, a, b and a.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://developer.apple.com/documentation/swiftui/uiviewrepresentable): Apple's SwiftUI documentation covers `UIViewRepresentable`, `NSViewRepresentable` and their coordinators; the language reference documents conditional compilation blocks.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-045: UIKit and AppKit integration boundaries.
Read courses/swift/guides/swift-045.md and courses/swift/lessons/swift-045.swift. Prerequisites: swift-044.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-045_solution.swift and
courses/swift/solutions/swift-045_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
