# swift-025: explanation and comparison

Reference program: [swift-025_solution.swift](swift-025_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Measure a fixed duration:** Explicit units prevent confusing minutes with the seconds expected by the API. The elapsed interval is 5,400 seconds.

**Parse equal instants with different offsets:** Offset information must be included when comparing wall-clock representations. Both strings represent the same instant.

## Task answers

### Task 1: Predict and explain

Convert the duration between seconds and minutes.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let seconds: TimeInterval = 5400
let minutes = seconds / 60
precondition(minutes == 90)
precondition(minutes * 60 == seconds)
let duration = Duration.seconds(5400)
precondition(duration.components.seconds / 60 == 90)
```

**Observe:** 5,400 seconds is 90 minutes, and 90 minutes converts back to exactly 5,400 seconds.

An elapsed duration is a count of seconds with no calendar involved, so dividing and multiplying by 60 converts losslessly in both directions.

### Task 2: Guided modification

Add a day-sized duration and explain why this is not a universal next-local-day rule.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
var calendar = Calendar(identifier: .gregorian)
calendar.timeZone = TimeZone(identifier: "America/New_York")!
let start = ISO8601DateFormatter().date(from: "2025-03-08T12:00:00-05:00")!
let plusSeconds = start.addingTimeInterval(86_400)
let nextLocalDay = calendar.date(byAdding: .day, value: 1, to: start)!
precondition(calendar.component(.hour, from: plusSeconds) == 13)
precondition(calendar.component(.hour, from: nextLocalDay) == 12)
precondition(nextLocalDay.timeIntervalSince(start) == 82_800)
```

**Observe:** Across the March 9 daylight-saving change in New York, adding 86,400 seconds lands at 13:00 local, while the calendar's next day is 12:00 and only 82,800 seconds later.

A fixed 86,400 seconds is an elapsed duration; next local day is a calendar question that depends on the time zone, and a 23-hour day breaks the equivalence.

### Task 3: Independent construction

Build a report from fixed timestamp fixtures.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
let formatter = ISO8601DateFormatter()
let start = formatter.date(from: "2025-03-01T22:30:00Z")!
let end = formatter.date(from: "2025-03-02T01:15:00Z")!
let minutes = Int(end.timeIntervalSince(start) / 60)
let report = "\(minutes) minutes from \(formatter.string(from: start))"
precondition(report == "165 minutes from 2025-03-01T22:30:00Z")
```

**Observe:** The report reads 165 minutes from 2025-03-01T22:30:00Z.

Fixed UTC fixtures make the duration independent of the machine's time zone, and the date change at midnight needs no special case.

### Task 4: Diagnose a defect

Diagnose treating an offset as a complete time-zone identity.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
let fixedOffset = TimeZone(secondsFromGMT: -5 * 3600)!
let newYork = TimeZone(identifier: "America/New_York")!
let parser = ISO8601DateFormatter()
let winter = parser.date(from: "2025-01-15T12:00:00Z")!
let summer = parser.date(from: "2025-07-15T12:00:00Z")!
precondition(fixedOffset.secondsFromGMT(for: winter) == newYork.secondsFromGMT(for: winter))
precondition(fixedOffset.secondsFromGMT(for: summer) == -18_000)
precondition(newYork.secondsFromGMT(for: summer) == -14_400)
```

**Observe:** In January the -05:00 offset and New York agree, but in July New York is -04:00 while the fixed offset stays -05:00.

An offset describes one instant; a time-zone identifier carries the rules that change the offset over the year, so storing -05:00 as the user's zone breaks future summer times.

### Task 5: Boundary evidence

Test an interval crossing midnight and malformed timestamp text.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
let parser = ISO8601DateFormatter()
let late = parser.date(from: "2025-01-01T23:50:00Z")!
let early = parser.date(from: "2025-01-02T00:10:00Z")!
precondition(early.timeIntervalSince(late) == 1200)
precondition(parser.date(from: "not a date") == nil)
precondition(parser.date(from: "2025-01-01T10:00:00") == nil)
```

**Observe:** 23:50 to 00:10 the next day is 1,200 seconds, while garbage text and a timestamp without an offset both parse to nil.

Instants subtract without regard to the date change at midnight, and the internet date-time format requires an offset, so incomplete text is refused instead of being guessed.

### Task 6: Transfer and justify

Design storage, display and duration-measurement policies for an appointment app.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** Example A starts at the Unix epoch and adds `90 * 60` seconds, then measures the interval. Example B parses two ISO 8601 strings, one with a +02:00 offset and one in UTC, and compares the resulting `Date` values. The task 3 answer builds a report from fixed timestamp fixtures.

**Why it is correct.** `addingTimeInterval` expects seconds, and 90 minutes times 60 is 5,400 seconds, so the measured interval is exactly 5400. Noon at +02:00 is 10:00 UTC, so both strings parse to the same instant and `first == second` holds. In task 3 the report reads 165 minutes from 2025-03-01T22:30:00Z, a span that crosses midnight.

**A plausible wrong approach.** Passing 90 to `addingTimeInterval` because the requirement says 90 minutes produces a 90-second span, and the 5400 check fails. Comparing the two timestamp strings as text would call them different, even though they describe one instant; a fixed offset like +02:00 also is not a time zone, since it says nothing about daylight-saving rules.

**How to verify.** Change one offset to +03:00 and confirm the equality check fails. For task 5, parse "2025-01-01 12:00" (no T and no offset) and confirm the formatter returns nil rather than guessing a time zone.

## Mechanism and diagnostic reasoning

Date represents an instant, independent of how a user sees it. Calendar and time-zone rules translate instants into local components. A fixed offset does not capture an entire region's daylight-saving history. Adding a duration and asking for the next calendar day can therefore answer different questions.

Use fixed instants in tests rather than the current machine clock. ISO 8601 is useful for exchanging timestamps, while localized formatting serves display. For performance measurement, use a monotonic clock rather than wall-clock time, which can be adjusted. Keep the unit of every duration explicit.

Date(timeIntervalSince1970:) constructs a fixed instant. addingTimeInterval uses seconds. ISO8601DateFormatter translates an exchange representation. Calendar operations require an explicit calendar and time zone for reproducible component reasoning.

Date has no inherent display time zone. Locale-sensitive formatting should not be used as an undocumented machine-data contract. Daylight-saving changes can create missing or repeated local times.

## Review before continuing

Run the reference and confirm it prints `swift-025: passed`, then rerun the guide's counterexample.
