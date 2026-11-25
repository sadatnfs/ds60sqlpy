# csharp-027: explanation and comparison

Reference program: [csharp-027_solution.cs](csharp-027_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Different offsets, same instant:** Comparing wall-clock components would miss the offset information. The values denote the same instant despite different offsets.

**Measure a fixed duration:** A fixed fixture keeps evidence independent of the host clock and locale. The elapsed duration is 90 minutes and the timestamp round-trips.

## Task answers

### Task 1: Predict and explain

Explain why the two offset timestamps compare equal.

**Written answer.** `a` is 12:00 at +02:00, which is 10:00 UTC, and `b` is 10:00 at UTC. `==` on `DateTimeOffset` compares the UTC instants, so they are equal, while `Offset` is 2 hours for `a` and 0 for `b`.

**Why it is correct.** A `DateTimeOffset` stores a local clock reading and its offset from UTC. Equality and ordering use `UtcDateTime`; the offset is kept only for display. `EqualsExact` is the method that also compares offsets.

**Plausible wrong approach.** Comparing `a.DateTime == b.DateTime` or `a.Hour == b.Hour` compares the wall-clock parts 12:00 and 10:00 and reports a two-hour difference between what is one instant.

**How to verify.** Add `Check(a.UtcDateTime == b.UtcDateTime, "same UTC");` and `Check(!a.EqualsExact(b), "offsets differ");`. Both pass beside the existing checks.

### Task 2: Guided modification

Change one instant by one minute and predict the comparison.

**Written answer.** Parse `a` as `2025-01-01T12:01:00+02:00`. Now `a == b` is false, `a > b` is true and `a - b` is exactly one minute.

**Why it is correct.** Subtraction and comparison convert both values to UTC first: 10:01 against 10:00.

**Plausible wrong approach.** Subtracting the wall-clock readings, 12:01 minus 10:00, predicts 121 minutes. That number is real only for two timestamps in the same offset, and these differ by two hours.

**How to verify.** Check `a - b == TimeSpan.FromMinutes(1)` and `a > b`; then change `b` to `10:01:00Z` and check that `a == b` is true again.

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

**Plausible wrong approach.** The interpolation `$"{elapsed.TotalMinutes} minutes"` formats a `double` with the current culture. 165 has no fractional part, but a 90.5-minute interval prints `90,5 minutes` under a culture such as `de-DE`, so machine-read reports should use `elapsed.TotalMinutes.ToString(CultureInfo.InvariantCulture)`.

**How to verify.** The block checks 165 minutes and the report text. Add `Check(elapsed.TotalHours == 2.75)` and check that `start - end` is `-165` minutes, which shows the sign follows the order of subtraction.

### Task 4: Diagnose a defect

Diagnose treating an offset as a complete time-zone identity.

**Written answer.** A stored `2025-01-10T09:00+01:00` for a Paris meeting fixes the offset, not the zone. `AddMonths(6)` keeps +01:00 and yields 09:00 at +01:00 in July, but Paris is then at +02:00, so the meeting shows as 10:00 local. Store the zone ID `Europe/Paris` and convert with `TimeZoneInfo`.

**Why it is correct.** An offset records how one moment relates to UTC. A time zone is a set of rules, including daylight-saving changes, that gives a different offset on different dates.

**Plausible wrong approach.** Storing only UTC and calling `ToLocalTime()` for display swaps one mistake for another: the result now depends on the zone of the machine running the code, so a server in UTC shows 08:00 for a 09:00 Paris meeting.

**How to verify.** On a machine with time zone data, check `TimeZoneInfo.FindSystemTimeZoneById("Europe/Paris").GetUtcOffset(new DateTime(2025, 7, 10))` is 2 hours while the January date gives 1 hour.

### Task 5: Boundary evidence

Test intervals across midnight and reject an end before its start when the domain forbids it.

**Written answer.** Write `TimeSpan Span(DateTimeOffset s, DateTimeOffset e) => e < s ? throw new ArgumentException("end before start") : e - s;`. Check 23:50Z to 00:10Z the next day is 20 minutes, equal start and end is `TimeSpan.Zero`, and reversed inputs throw.

**Why it is correct.** Subtracting full `DateTimeOffset` values includes the date, so midnight is not a special case. The guard turns a negative duration into a rejection when the domain forbids it.

**Plausible wrong approach.** Computing from `e.TimeOfDay - s.TimeOfDay` drops the dates: 00:10 minus 23:50 is minus 23 hours 40 minutes, so the guard rejects a valid 20-minute interval as ending before its start.

**How to verify.** Run the three checks with fixed UTC values, catching `ArgumentException` for the reversed pair.

### Task 6: Transfer and justify

Design storage and display policies for appointments in a named time zone.

**Written answer.** For future appointments, store the local date and time plus a zone ID such as `America/New_York`, and compute the UTC instant when needed. Display by converting to the viewer's zone. For events that already happened, store the UTC instant.

**Why it is correct.** A 09:00 meeting should stay at 09:00 local even if daylight-saving rules change before it happens. Storing the zone keeps that intent; converting at display time keeps viewers correct. Invalid and repeated local times must be handled at booking.

**Plausible wrong approach.** Converting the booking to a UTC instant at creation freezes the rules in force that day. If they change, the stored instant now displays as 08:00 or 10:00 local, and nothing in storage records that 09:00 was intended.

**How to verify.** With `var ny = TimeZoneInfo.FindSystemTimeZoneById("America/New_York");`, check `ny.IsInvalidTime(new DateTime(2025, 3, 9, 2, 30, 0))` is true and `ny.IsAmbiguousTime(new DateTime(2025, 11, 2, 1, 30, 0))` is true, and make the booking code reject or clarify both.

## Mechanism and diagnostic reasoning

An instant, a local wall-clock time and a duration are different concepts. DateTimeOffset combines a date-time with an offset, making an instant comparison explicit. A time-zone identifier carries additional historical daylight-saving rules that a fixed offset does not. Do not infer a region from its offset alone.

A duration measures elapsed time; a calendar rule such as next month follows calendar boundaries. Persist machine-readable data using a stable format and parse with an explicit culture. User-facing formatting may intentionally vary by locale. Tests should fix their clock inputs rather than depend on the date or local zone of the machine running them.

`DateTimeOffset.Parse` with an explicit round-trip string creates a known instant. `ToUniversalTime` changes its display offset while retaining the instant. Subtraction produces TimeSpan. InvariantCulture avoids environment-dependent machine-data parsing.

DateTime kind and unspecified local values can introduce ambiguity. Daylight-saving transitions can produce invalid or repeated local times. Use elapsed-time clocks for performance measurement, not wall-clock timestamps.

## Review before continuing

Run the reference and confirm it prints `csharp-027: passed`, then rerun the guide's counterexample.
