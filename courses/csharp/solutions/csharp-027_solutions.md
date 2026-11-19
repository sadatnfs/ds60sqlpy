# csharp-027: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-027_solution.cs](csharp-027_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Different offsets, same instant:** Comparing wall-clock components would miss the offset information. The values denote the same instant despite different offsets.

**Measure a fixed duration:** A fixed fixture keeps evidence independent of the host clock and locale. The elapsed duration is 90 minutes and the timestamp round-trips.

## Task answers

### Task 1: Predict and explain

Explain why the two offset timestamps compare equal.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Comparing wall-clock components would miss the offset information. The values denote the same instant despite different offsets.

### Task 2: Guided modification

Change one instant by one minute and predict the comparison.

No separate reference answer has been written for this task. Start from Example B: A fixed fixture keeps evidence independent of the host clock and locale. The elapsed duration is 90 minutes and the timestamp round-trips.

### Task 3: Independent construction

Build a duration report using fixed UTC timestamps.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
var start = new DateTimeOffset(2025, 3, 1, 22, 30, 0, TimeSpan.Zero);
var end = new DateTimeOffset(2025, 3, 2, 1, 15, 0, TimeSpan.Zero);
TimeSpan elapsed = end - start;
string report = $"{elapsed.TotalMinutes} minutes";
Check(elapsed == TimeSpan.FromMinutes(165), "across midnight");
Check(report == "165 minutes", "invariant report");
```

**Observe:** 22:30 to 01:15 UTC is reported as 165 minutes.

Fixed UTC instants make the duration independent of the machine's time zone, and subtraction handles the date change.

### Task 4: Diagnose a defect

Diagnose treating an offset as a complete time-zone identity.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: DateTime kind and unspecified local values can introduce ambiguity. Daylight-saving transitions can produce invalid or repeated local times. Use elapsed-time clocks for performance measurement, not wall-clock timestamps.

### Task 5: Boundary evidence

Test intervals across midnight and reject an end before its start when the domain forbids it.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Different offsets, same instant) and Example B (Measure a fixed duration).

### Task 6: Transfer and justify

Design storage and display policies for appointments in a named time zone.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Instant**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

An instant, a local wall-clock time and a duration are different concepts. DateTimeOffset combines a date-time with an offset, making an instant comparison explicit. A time-zone identifier carries additional historical daylight-saving rules that a fixed offset does not. Do not infer a region from its offset alone.

A duration measures elapsed time; a calendar rule such as next month follows calendar boundaries. Persist machine-readable data using a stable format and parse with an explicit culture. User-facing formatting may intentionally vary by locale. Tests should fix their clock inputs rather than depend on the date or local zone of the machine running them.

`DateTimeOffset.Parse` with an explicit round-trip string creates a known instant. `ToUniversalTime` changes its display offset while retaining the instant. Subtraction produces TimeSpan. InvariantCulture avoids environment-dependent machine-data parsing.

DateTime kind and unspecified local values can introduce ambiguity. Daylight-saving transitions can produce invalid or repeated local times. Use elapsed-time clocks for performance measurement, not wall-clock timestamps.

## Review before continuing

Run the reference and confirm that it prints `csharp-027: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
