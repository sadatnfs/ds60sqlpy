# swift-025: Dates, calendars and elapsed time

## Level and prerequisites

Intermediate, approximately 90 minutes. Prerequisites: `swift-024`

## Learning objectives

Handle dates, calendars and elapsed time with fixed fixtures independent of the time zone. The central exercise is task 3: Build a report from fixed timestamp fixtures.

## Purpose and mental model

Date represents an instant, independent of how a user sees it. Calendar and time-zone rules translate instants into local components. A fixed offset does not capture an entire region's daylight-saving history. Adding a duration and asking for the next calendar day can therefore answer different questions.

Use fixed instants in tests rather than the current machine clock. ISO 8601 is useful for exchanging timestamps, while localized formatting serves display. For performance measurement, use a monotonic clock rather than wall-clock time, which can be adjusted. Keep the unit of every duration explicit.

## Vocabulary and concepts

**Instant:** A point on the time line.

**Calendar:** Rules mapping instants to civil date components.

**Monotonic clock:** A clock suitable for elapsed time without wall-clock adjustments.

## How to run this lesson

Both examples use fixed timestamps, so they give the same answer on every machine and in every time zone. Avoid `Date()` in your own checks for the same reason: the current time makes a check pass today and fail tomorrow. Task 5 includes malformed text, and `ISO8601DateFormatter.date(from:)` returns nil for it rather than throwing.

Compile contract, starter stop and success marker: [running a lesson](../STUDY-GUIDE.md#running-a-lesson).



## Syntax anatomy and execution trace

Date(timeIntervalSince1970:) constructs a fixed instant. addingTimeInterval uses seconds. ISO8601DateFormatter translates an exchange representation. Calendar operations require an explicit calendar and time zone for reproducible component reasoning.

Each example ends with a trace; method: [tracing a program](../STUDY-GUIDE.md#tracing-a-program).

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

**Trace.** `Date(timeIntervalSince1970: 0)` is the instant 1970-01-01 at midnight UTC, chosen only because it is easy to write. `90 * 60` converts 90 minutes into 5400 seconds, the unit `TimeInterval` always uses. `addingTimeInterval` returns a new date 5400 seconds later and leaves `start` alone. `timeIntervalSince` subtracts in the other direction and returns 5400.0. The comparison is exact because both values are whole seconds well within the precision of a `Double`, so no tolerance is needed here.

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

**Trace.** The formatter parses the first string as noon at an offset of plus two hours, which is 10:00 in UTC. It parses the second, whose Z suffix means UTC, as exactly 10:00. Both calls return a `Date`, and a `Date` stores only an absolute instant with no offset or zone attached, so the two values compare equal. The check also confirms the first parse did not return nil, because comparing two nil results would pass too and prove nothing.

## Exercises

1. **Predict and explain.** Convert the duration between seconds and minutes.

2. **Guided modification.** Add a day-sized duration and explain why this is not a universal next-local-day rule.

3. **Independent construction.** Build a report from fixed timestamp fixtures.

4. **Diagnose a defect.** Diagnose treating an offset as a complete time-zone identity.

5. **Boundary evidence.** Test an interval crossing midnight and malformed timestamp text.

6. **Transfer and justify.** Design storage, display and duration-measurement policies for an appointment app.

Log each task in the [evidence table](../STUDY-GUIDE.md#recording-exercise-evidence) before opening the explanation.

## Common pitfalls and diagnosis

Date has no inherent display time zone. Locale-sensitive formatting should not be used as an undocumented machine-data contract. Daylight-saving changes can create missing or repeated local times.

For task 4, two strings with the same offset can belong to different zones. The counterexample uses one offset at two dates: +01:00 is Paris in January, but in July Paris uses +02:00 while Lagos stays at +01:00. Storing only the offset cannot recover which rule applies next week. For task 5, an interval from 23:30 to 00:15 the next day must be 2700 seconds, not negative.

Repair routine: [building a regression case](../STUDY-GUIDE.md#building-a-regression-case).

## Progressive hints

1. Reproduce Example A (Measure a fixed duration) before changing anything, and confirm its observation: The elapsed interval is 5,400 seconds.
2. Compare Example B (Parse equal instants with different offsets) with Example A and name the first line whose behavior differs. Its observation is: Both strings represent the same instant.
3. Before opening the explanation, check your task 3 attempt (Build a report from fixed timestamp fixtures) against each pitfall listed above, and add one input that would expose the tempting wrong rule.

## Self-check and next step

Explain why `Date` comparison ignores the offset printed in the original text. State the number of seconds in 90 minutes and in one day, then explain why adding the one-day figure does not always land on the same local clock time tomorrow. Say what an appointment app should store to show a meeting correctly after a daylight-saving change.

Then follow the general [self-check routine](../STUDY-GUIDE.md#self-check-routine) and save your pad.

## Sources and execution boundary

[Documentation](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/): Read the Foundation reference pages for `Date`, `TimeInterval`, `ISO8601DateFormatter` and `TimeZone`, and the `Calendar` page for adding calendar days.

Provenance and limits: [sources and execution boundary](../STUDY-GUIDE.md#sources-and-execution-boundary).

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
