# swift-045: UIKit and AppKit integration boundaries

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-044`

## Learning objectives

Inspect and build SelectableText.swift in the Apple project. Then document coordinator ownership, delegate cleanup and platform-specific API availability.

## Purpose and mental model

SwiftUI can host platform-native views through representable adapters. UIKit serves iOS-family interfaces, while AppKit serves macOS. These frameworks do not exist inside the Linux worker. The adapter translates value-driven SwiftUI updates into an imperative view lifecycle and translates callbacks back into application actions.

A coordinator commonly owns delegate behavior. It must avoid feedback loops where a programmatic update triggers the same callback as a user edit and repeatedly writes state. Keep identity and lifetime explicit, and release delegates or observers when the view is dismantled. The fixture includes actual conditional UIKit and AppKit bridge source for a selectable text view.

## Vocabulary and concepts

**Representable adapter:** A SwiftUI bridge to an imperative platform view.

**Coordinator:** An object owning delegate or callback integration.

**Feedback loop:** An update triggering a callback that repeats the same update indefinitely.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.

The complete [JourneyApp fixture](../fixtures/JourneyApp/README.md) contains `SelectableText.swift` with real UIKit and AppKit representable implementations.

## Syntax anatomy and execution trace

UIViewRepresentable uses makeUIView and updateUIView. NSViewRepresentable has corresponding AppKit methods. A Coordinator bridges delegate callbacks. Compile-time canImport guards select the appropriate platform source.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

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

## Exercises

1. **Predict and explain.** Identify the value-driven and imperative sides of the bridge.

2. **Guided modification.** Add a no-op case and verify no extra assignment.

3. **Independent construction.** Inspect and build SelectableText.swift in the Apple project.

4. **Diagnose a defect.** Diagnose an update callback that writes the same binding recursively.

5. **Boundary evidence.** Test empty text, large text and repeated updates in the platform view.

6. **Transfer and justify.** Document coordinator ownership, delegate cleanup and platform-specific API availability.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

A canImport branch is not evidence that both platforms were tested. UIKit and AppKit lifecycles differ. Avoid retaining transient SwiftUI view values as permanent controller state.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Representable adapter, Coordinator, Feedback loop without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://developer.apple.com/documentation/swiftui/uiviewrepresentable). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
