# swift-043: Networking, loading states and stale-result protection

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-042`

## Learning objectives

Model loading states and discard stale network results with a deterministic fake transport. The central exercise is task 3: Implement a deterministic fake transport returning success and failure values.

## Purpose and mental model

A network-backed view needs more states than a Boolean loading flag. Idle, loading, ready and failed states carry different information and should be rendered honestly. Cancellation of an old request can reduce work, but a stale response can still arrive if the operation does not cooperate. A request generation or identity check prevents an older result from overwriting newer intent.

URLSession is a Foundation API with platform differences: Linux networking code requires FoundationNetworking. The ordinary pad uses an injected deterministic data source and a pure acceptance rule, so it contacts no server. The app lab explains where a real transport adapter belongs, with status, size, schema and cancellation checks before admission.

## Vocabulary and concepts

**Loading state:** A model of request progress and result category.

**Stale result:** A response belonging to superseded user intent.

**Transport adapter:** The component responsible for actual network exchange.

## How to run this lesson

The pad stays offline; `LoadState` is a pure kernel declared above `LessonMain`. Task 3 uses a fake transport that returns canned values, so every test is deterministic. Task 5's network cases belong in a separately prepared adapter, and on Linux `URLSession` requires `import FoundationNetworking`.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).

The [JourneyApp project notes](../fixtures/JourneyApp/README.md) provide the exact seam for a separately prepared network adapter. The default app and pad remain offline.

## Syntax anatomy and execution trace

A request generation increments when intent changes. Accept a result only if its generation still matches current state. A transport protocol can return Data for a validated decoder while keeping the UI model independent of URLSession.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

**Trace.** `state` starts at generation 2 with no title. The call `accept("new", generation: 2)` reaches the guard, which compares the candidate 2 with the current 2 and passes. The method stores new as the title. The check confirms it. The generation number represents the most recent intent, such as the latest search text, and only a result tagged with that number may change state.

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

**Trace.** `state` is at generation 2 and already shows new. A late reply from an earlier request arrives tagged with generation 1. The guard sees 1 differs from 2 and returns without changing anything, so the title stays new. Cancelling the old request would not have been enough: it might complete anyway, and this guard makes a late arrival harmless whatever the network did.

## Exercises

1. **Predict and explain.** Trace current intent and result identity.

2. **Guided modification.** Advance the generation and accept only the new response.

3. **Independent construction.** Implement a deterministic fake transport returning success and failure values.

4. **Diagnose a defect.** Diagnose an old search response replacing a newer search result.

5. **Boundary evidence.** Test empty data, malformed data, non-success status and cancellation separately in the prepared adapter.

6. **Transfer and justify.** Design a URLSession boundary with explicit FoundationNetworking import on Linux, request timeout, size bound and schema validation.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

An awaited response is not automatically a successful HTTP status. Never assume cancellation prevents all late callbacks. Avoid logging authorization headers or raw private response bodies.

Task 4's bug appears when replies arrive out of order: start a search for a, then for ab, and let the reply for a arrive last. Without the guard the screen shows results for a while the field says ab. The counterexample delivers the newer reply first, then the older one, and checks the newer value survives. For task 2, advance to 3 and confirm a reply tagged 2 is ignored.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Accept the current request result) before changing anything, and confirm its observation: The matching generation updates current state.
2. Compare Example B (Ignore a superseded result) with Example A and name the first line whose behavior differs. Its observation is: The stale response cannot overwrite the newer value.
3. Before opening the explanation, check your task 3 attempt (Implement a deterministic fake transport returning success and failure values) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain why a generation check is needed even when the old request is cancelled. Describe what a fake transport must return to test success, failure and malformed data separately. List the timeout, size limit and validation steps a real `URLSession` adapter should apply before decoding.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://developer.apple.com/documentation/foundation/urlsession): The Foundation reference documents `URLSession` and `URLRequest`; swift-corelibs-foundation explains the separate FoundationNetworking module on Linux.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
