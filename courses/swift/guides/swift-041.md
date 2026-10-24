# swift-041: Navigation, stable identity and deep-link validation

## Level and prerequisites

Advanced, approximately 120 minutes. Prerequisites: `swift-040`

## Learning objectives

Run JourneyApp and navigate by stable item identity. Then design a restoration format for navigation without storing view instances or private payloads.

## Purpose and mental model

Navigation is application state, not just an animation. A route should identify a destination with stable data rather than retaining a transient view instance. Typed route values make allowed destinations explicit and easier to test. If an item disappears, the app needs a clear missing-destination state.

A deep link is external input. Parse its scheme, host and path under an explicit allowlist and resolve resource identity through the model. Do not let arbitrary URL text choose a file path or execute a command. The app fixture uses NavigationStack and value-based destinations; the portable example checks route parsing independently of Apple rendering.

## Vocabulary and concepts

**Route:** A typed description of an application destination.

**Deep link:** An external address requesting a particular application location.

**Navigation path:** An ordered stack of route values.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.

The [JourneyApp project](../fixtures/JourneyApp/README.md) includes a real NavigationStack and missing-item view. URL parsing in the pad is only the portable routing kernel.

## Syntax anatomy and execution trace

A Hashable Route enum can back a NavigationStack path. URLComponents exposes parsed URL fields. A route parser should return an optional or error for unrecognized shapes.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Parse an admitted route

The parser translates untrusted text into a limited domain route.

```swift
import Foundation

enum Route: Hashable { case item(String) }
func parseRoute(_ text: String) -> Route? { guard let url = URLComponents(string: text), url.scheme == "journey", url.host == "item", url.query == nil, url.fragment == nil else { return nil }; let parts = url.path.split(separator: "/"); guard parts.count == 1 else { return nil }; return .item(String(parts[0])) }

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

### Example B: Reject unrelated or incomplete links

A route parser is an allowlist, not a generic command interpreter.

```swift
import Foundation

enum Route: Hashable { case item(String) }
func parseRoute(_ text: String) -> Route? { guard let url = URLComponents(string: text), url.scheme == "journey", url.host == "item", url.query == nil, url.fragment == nil else { return nil }; let parts = url.path.split(separator: "/"); guard parts.count == 1 else { return nil }; return .item(String(parts[0])) }

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

## Exercises

1. **Predict and explain.** Trace each URL component into the route decision.

2. **Guided modification.** Add a separate explicit overview route.

3. **Independent construction.** Run JourneyApp and navigate by stable item identity.

4. **Diagnose a defect.** Diagnose navigation keyed by array position after reordering.

5. **Boundary evidence.** Test a missing item identity and an item deleted while its route is open.

6. **Transfer and justify.** Design a restoration format for navigation without storing view instances or private payloads.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Parsing a URL does not authorize access. Array offsets are unstable identities. Never route arbitrary URL text directly into file access or shell commands.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Route, Deep link, Navigation path without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://developer.apple.com/documentation/swiftui/navigationstack). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

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
