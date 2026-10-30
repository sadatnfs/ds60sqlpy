# swift-043: Networking, loading states and stale-result protection

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-042`

## Learning objectives

Implement a deterministic fake transport returning success and failure values. Then design a URLSession boundary with explicit FoundationNetworking import on Linux, request timeout, size bound and schema validation.

## Purpose and mental model

A network-backed view needs more states than a Boolean loading flag. Idle, loading, ready and failed states carry different information and should be rendered honestly. Cancellation of an old request can reduce work, but a stale response can still arrive if the operation does not cooperate. A request generation or identity check prevents an older result from overwriting newer intent.

URLSession is a Foundation API with platform differences: Linux networking code requires FoundationNetworking. The ordinary pad uses an injected deterministic data source and a pure acceptance rule, so it contacts no server. The app lab explains where a real transport adapter belongs, with status, size, schema and cancellation checks before admission.

## Vocabulary and concepts

**Loading state:** A model of request progress and result category.

**Stale result:** A response belonging to superseded user intent.

**Transport adapter:** The component responsible for actual network exchange.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.

The [JourneyApp project notes](../fixtures/JourneyApp/README.md) provide the exact seam for a separately prepared network adapter. The default app and pad remain offline.

## Syntax anatomy and execution trace

A request generation increments when intent changes. Accept a result only if its generation still matches current state. A transport protocol can return Data for a validated decoder while keeping the UI model independent of URLSession.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Accept the current request result

Identity connects a result to the intent that authorized it.

```swift
import Foundation

struct LoadState {
  var generation: Int
  var title: String?
  mutating func accept(_ value: String, generation candidate: Int) {
    guard candidate == generation else { return }
    title = value
  }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      var state = LoadState(generation: 2, title: nil)
      state.accept("new", generation: 2)
      precondition(state.title == "new")
    }
    print("swift-043: passed")
  }
}
```

**Observe:** The matching generation updates current state.

### Example B: Ignore a superseded result

Cancellation alone would not establish this guarantee because an operation may still complete.

```swift
import Foundation

struct LoadState {
  var generation: Int
  var title: String?
  mutating func accept(_ value: String, generation candidate: Int) {
    guard candidate == generation else { return }
    title = value
  }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      var state = LoadState(generation: 2, title: "new")
      state.accept("old", generation: 1)
      precondition(state.title == "new")
    }
    print("swift-043: passed")
  }
}
```

**Observe:** The stale response cannot overwrite the newer value.

## Exercises

1. **Predict and explain.** Trace current intent and result identity.

2. **Guided modification.** Advance the generation and accept only the new response.

3. **Independent construction.** Implement a deterministic fake transport returning success and failure values.

4. **Diagnose a defect.** Diagnose an old search response replacing a newer search result.

5. **Boundary evidence.** Test empty data, malformed data, non-success status and cancellation separately in the prepared adapter.

6. **Transfer and justify.** Design a URLSession boundary with explicit FoundationNetworking import on Linux, request timeout, size bound and schema validation.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

An awaited response is not automatically a successful HTTP status. Never assume cancellation prevents all late callbacks. Avoid logging authorization headers or raw private response bodies.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Loading state, Stale result, Transport adapter without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://developer.apple.com/documentation/foundation/urlsession). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-043: Networking, loading states and stale-result protection.
Read courses/swift/guides/swift-043.md and courses/swift/lessons/swift-043.swift. Prerequisites: swift-042.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-043_solution.swift and
courses/swift/solutions/swift-043_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
