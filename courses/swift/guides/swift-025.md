# swift-025: Dates, calendars and elapsed time

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-024`

## Learning objectives

Build a report from fixed timestamp fixtures. Then design storage, display and duration-measurement policies for an appointment app.

## Purpose and mental model

Date represents an instant, independent of how a user sees it. Calendar and time-zone rules translate instants into local components. A fixed offset does not capture an entire region's daylight-saving history. Adding a duration and asking for the next calendar day can therefore answer different questions.

Use fixed instants in tests rather than the current machine clock. ISO 8601 is useful for exchanging timestamps, while localized formatting serves display. For performance measurement, use a monotonic clock rather than wall-clock time, which can be adjusted. Keep the unit of every duration explicit.

## Vocabulary and concepts

**Instant:** A point on the time line.

**Calendar:** Rules mapping instants to civil date components.

**Monotonic clock:** A clock suitable for elapsed time without wall-clock adjustments.

## How to run this lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. An explicit `@main` type contains `static func main() async throws`; the fixed compiler uses `-parse-as-library -swift-version 6`. The examples use the standard library and portable Foundation. `precondition` makes a violated invariant fail the process. The fixed pad accepts one source file, without arbitrary command arguments, interactive input or dependency installation. SwiftUI, UIKit, Apple simulators and application signing belong to the separately prepared macOS/Xcode project labs, never the Linux pad.

Start with the answer-free learner artifact in your saved classroom pad. It deliberately reports that the task remains unfinished. Replace its stop with your implementation. The worked programs below are independently complete: copy one at a time into a separate exploratory pad if useful. The reference combines both scenarios and their checked boundary observations. Successful checks are silent; the final lesson marker appears only after they complete. A marker is execution evidence for these fixtures, not an automatic assessment of your understanding.



## Syntax anatomy and execution trace

Date(timeIntervalSince1970:) constructs a fixed instant. addingTimeInterval uses seconds. ISO8601DateFormatter translates an exchange representation. Calendar operations require an explicit calendar and time zone for reproducible component reasoning.

Read the operations in dependency order. Record which values exist before each line, which expression produces a new value, and which operation changes shared state. When the compiler rejects source, no later runtime observation exists. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. These two situations need different repairs.

## Worked example / walkthrough

### Example A: Measure a fixed duration

Explicit units prevent confusing minutes with the seconds expected by the API.

```swift
import Foundation



@main
struct LessonMain {
    static func main() async throws {
        do {
            let start = Date(timeIntervalSince1970: 0)
            let end = start.addingTimeInterval(90 * 60)
            precondition(end.timeIntervalSince(start) == 5400)
        }
        print("swift-025: passed")
    }
}
```

**Observe:** The elapsed interval is 5,400 seconds.

### Example B: Parse equal instants with different offsets

Offset information must be included when comparing wall-clock representations.

```swift
import Foundation



@main
struct LessonMain {
    static func main() async throws {
        do {
            let formatter = ISO8601DateFormatter()
            let first = formatter.date(from: "2025-01-01T12:00:00+02:00")
            let second = formatter.date(from: "2025-01-01T10:00:00Z")
            precondition(first != nil && first == second)
        }
        print("swift-025: passed")
    }
}
```

**Observe:** Both strings represent the same instant.

## Exercises

1. **Predict and explain.** Convert the duration between seconds and minutes.

2. **Guided modification.** Add a day-sized duration and explain why this is not a universal next-local-day rule.

3. **Independent construction.** Build a report from fixed timestamp fixtures.

4. **Diagnose a defect.** Diagnose treating an offset as a complete time-zone identity.

5. **Boundary evidence.** Test an interval crossing midnight and malformed timestamp text.

6. **Transfer and justify.** Design storage, display and duration-measurement policies for an appointment app.

For each task, keep a short evidence table: input or initial state, prediction, observed value or diagnostic, and the rule that explains it. The guided examples establish mechanisms; the independent and transfer tasks require your own representation and explanation. Use the separate solution after attempting the task, then close it and reconstruct one boundary case.

## Common pitfalls and diagnosis

Date has no inherent display time zone. Locale-sensitive formatting should not be used as an undocumented machine-data contract. Daylight-saving changes can create missing or repeated local times.

A useful regression case distinguishes the intended rule from the tempting wrong rule. Check both the original example and the smallest counterexample after a repair. Do not convert an error into a plausible default unless the contract explicitly assigns that meaning. Keep resource cleanup and failure propagation visible whenever the example owns a file, task or other resource.

## Progressive hints

1. Name the input, output and invariant using the vocabulary above. Reproduce Example A before changing two things at once.
2. Compare the changed condition in Example B. Identify the first line whose behavior differs and state why.
3. Reduce your independent task to a normal case, an empty or boundary case, and an invalid case. Write expected observations before inspecting the reference.

## Self-check and next step

Explain Instant, Calendar, Monotonic clock without reading the definitions. Reconstruct a small example from a blank file and choose an input not used in this chapter. State one cost or limitation of the technique. Save the working pad and your reasoning before moving to the next lesson; later chapters build on these contracts.

## Sources and execution boundary

[Official language or framework documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/). The prose, small fixtures and task designs in this chapter are original. Documentation links provide additional API detail, not a dependency fetched by the classroom. Runtime qualification is recorded separately by the repository validation workflow. Reading a guide, compiling a reference, running its assertions and completing an external project are distinct achievements.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for swift-025: Dates, calendars and elapsed time.
Read courses/swift/guides/swift-025.md and courses/swift/lessons/swift-025.swift. Prerequisites: swift-024.
Teach the vocabulary and trace one example. Ask for my prediction before running.
Give one progressive hint about my first incorrect assumption. Review compiler
or runtime evidence and ask a fresh transfer question. Keep courses/swift/solutions/swift-025_solution.swift and
courses/swift/solutions/swift-025_solutions.md closed until I request comparison or show an attempt.
Use swift-linux for portable code. Separately labeled project labs keep their own
platform and preparation requirements. Completion requires explaining the
mechanism and all six task outcomes, not merely copying the success marker.
```
