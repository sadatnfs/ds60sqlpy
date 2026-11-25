# swift-041: Navigation, stable identity and deep-link validation

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-040`

## Learning objectives

Navigate by stable identity and validate deep links before acting on them. The central exercise is task 3: Run JourneyApp and navigate by stable item identity.

## Purpose and mental model

Navigation is application state, not just an animation. A route should identify a destination with stable data rather than retaining a transient view instance. Typed route values make allowed destinations explicit and easier to test. If an item disappears, the app needs a clear missing-destination state.

A deep link is external input. Parse its scheme, host and path under an explicit allowlist and resolve resource identity through the model. Do not let arbitrary URL text choose a file path or execute a command. The app fixture uses NavigationStack and value-based destinations; the portable example checks route parsing independently of Apple rendering.

## Vocabulary and concepts

**Route:** A typed description of an application destination.

**Deep link:** An external address requesting a particular application location.

**Navigation path:** An ordered stack of route values.

## How to run this lesson

Both examples declare `Route` and `parseRoute` above `LessonMain`. The parser is pure, so you can add more `precondition` lines for task 5's inputs without any app. Tasks 3 and 5's deleted-item case need JourneyApp's NavigationStack on an Apple platform.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).

The [JourneyApp project](../fixtures/JourneyApp/README.md) includes a real NavigationStack and missing-item view. URL parsing in the pad is only the portable routing kernel.

## Syntax anatomy and execution trace

A Hashable Route enum can back a NavigationStack path. URLComponents exposes parsed URL fields. A route parser should return an optional or error for unrecognized shapes.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

## Worked example / walkthrough

### Example A: Parse an admitted route

The parser translates untrusted text into a limited domain route.

```swift
import Foundation

enum Route: Hashable { case item(String) }
func parseRoute(_ text: String) -> Route? {
  guard let url = URLComponents(string: text), url.scheme == "journey", url.host == "item",
    url.query == nil, url.fragment == nil
  else { return nil }
  let parts = url.path.split(separator: "/")
  guard parts.count == 1 else { return nil }
  return .item(String(parts[0]))
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let route = parseRoute("journey://item/one")
      precondition(route == .item("one"))
    }
    print("swift-041: passed")
  }
}
```

**Observe:** The admitted scheme and host resolve to item one.

**Trace.** `URLComponents` splits the text into scheme journey, host item and path /one, with no query or fragment. The guard checks each against the allowlist and passes. Splitting the path on slashes drops the empty leading piece and gives one part, one. The count guard passes, and the function returns `.item("one")`, which equals the expected route because `Route` is `Hashable` and therefore `Equatable`.

### Example B: Reject unrelated or incomplete links

A route parser is an allowlist, not a generic command interpreter.

```swift
import Foundation

enum Route: Hashable { case item(String) }
func parseRoute(_ text: String) -> Route? {
  guard let url = URLComponents(string: text), url.scheme == "journey", url.host == "item",
    url.query == nil, url.fragment == nil
  else { return nil }
  let parts = url.path.split(separator: "/")
  guard parts.count == 1 else { return nil }
  return .item(String(parts[0]))
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      precondition(parseRoute("https://example.invalid/one") == nil)
      precondition(parseRoute("journey://item/") == nil)
      precondition(parseRoute("journey://delete/one") == nil)
    }
    print("swift-041: passed")
  }
}
```

**Observe:** Unrelated schemes, missing identity and unlisted actions are rejected.

**Trace.** For the https link the scheme check fails, so the parser returns nil before reading anything else. For journey://item/ the scheme and host pass, but the path is a single slash, which splits into zero parts, and the count guard returns nil. For journey://delete/one the host is delete, not item, so it fails the first guard. Every rejection is a nil result rather than a crash or a guessed route.

## Exercises

1. **Predict and explain.** Trace each URL component into the route decision.

2. **Guided modification.** Add a separate explicit overview route.

3. **Independent construction.** Run JourneyApp and navigate by stable item identity.

4. **Diagnose a defect.** Diagnose navigation keyed by array position after reordering.

5. **Boundary evidence.** Test a missing item identity and an item deleted while its route is open.

6. **Transfer and justify.** Design a restoration format for navigation without storing view instances or private payloads.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Parsing a URL does not authorize access. Array offsets are unstable identities. Never route arbitrary URL text directly into file access or shell commands.

`URLComponents` preserves the case of the scheme, so `JOURNEY://item/one` is rejected by this exact comparison even though URL schemes are case-insensitive; decide whether to lowercase first and test it. journey://item/a/b has two path parts and must be rejected. For task 4, a route stored as an array position opens the wrong item after reordering, while one keyed by identity still opens the right one.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Parse an admitted route) before changing anything, and confirm its observation: The admitted scheme and host resolve to item one.
2. Compare Example B (Reject unrelated or incomplete links) with Example A and name the first line whose behavior differs. Its observation is: Unrelated schemes, missing identity and unlisted actions are rejected.
3. Before opening the explanation, check your task 3 attempt (Run JourneyApp and navigate by stable item identity) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Trace journey://item/one?x=1 through the parser and state which guard rejects it. Explain why a parser for untrusted links should be an allowlist. Describe what the app should show when a route names an item that was deleted while its screen was open.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://developer.apple.com/documentation/swiftui/navigationstack): Read Apple's Foundation reference for `URLComponents` and SwiftUI's `NavigationStack` and `NavigationPath` pages.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-041: Navigation, stable identity and deep-link validation.
Read courses/swift/guides/swift-041.md and courses/swift/lessons/swift-041.swift. Prerequisites: swift-040.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-041_solution.swift and
courses/swift/solutions/swift-041_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
