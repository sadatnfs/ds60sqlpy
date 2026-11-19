# swift-025: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-025_solution.swift](swift-025_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Measure a fixed duration:** Explicit units prevent confusing minutes with the seconds expected by the API. The elapsed interval is 5,400 seconds.

**Parse equal instants with different offsets:** Offset information must be included when comparing wall-clock representations. Both strings represent the same instant.

## Task answers

### Task 1: Predict and explain

Convert the duration between seconds and minutes.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Explicit units prevent confusing minutes with the seconds expected by the API. The elapsed interval is 5,400 seconds.

### Task 2: Guided modification

Add a day-sized duration and explain why this is not a universal next-local-day rule.

No separate reference answer has been written for this task. Start from Example B: Offset information must be included when comparing wall-clock representations. Both strings represent the same instant.

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

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Date has no inherent display time zone. Locale-sensitive formatting should not be used as an undocumented machine-data contract. Daylight-saving changes can create missing or repeated local times.

### Task 5: Boundary evidence

Test an interval crossing midnight and malformed timestamp text.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Measure a fixed duration) and Example B (Parse equal instants with different offsets).

### Task 6: Transfer and justify

Design storage, display and duration-measurement policies for an appointment app.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Instant**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Date represents an instant, independent of how a user sees it. Calendar and time-zone rules translate instants into local components. A fixed offset does not capture an entire region's daylight-saving history. Adding a duration and asking for the next calendar day can therefore answer different questions.

Use fixed instants in tests rather than the current machine clock. ISO 8601 is useful for exchanging timestamps, while localized formatting serves display. For performance measurement, use a monotonic clock rather than wall-clock time, which can be adjusted. Keep the unit of every duration explicit.

Date(timeIntervalSince1970:) constructs a fixed instant. addingTimeInterval uses seconds. ISO8601DateFormatter translates an exchange representation. Calendar operations require an explicit calendar and time zone for reproducible component reasoning.

Date has no inherent display time zone. Locale-sensitive formatting should not be used as an undocumented machine-data contract. Daylight-saving changes can create missing or repeated local times.

## Review before continuing

Run the reference and confirm that it prints `swift-025: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
