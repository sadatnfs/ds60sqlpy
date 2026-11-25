# java-015: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

Time has several meanings. Instant identifies a point on the UTC timeline. LocalDate describes a calendar date without a time zone. LocalDateTime is a wall-clock reading that may be ambiguous or nonexistent in a region because of daylight-saving transitions. ZonedDateTime combines local fields with a zone and resolved offset. A calendar day is not always 24 elapsed hours. Store the meaning required by the domain rather than treating every timestamp as interchangeable text. Parse explicit offsets for event instants, and use a region zone when calendar rules matter.

**Instant:** A point on the UTC timeline.

**Local date-time:** Calendar and clock fields without a resolved zone offset.

**Zone rule:** A region-specific mapping between local time and offsets.

## Reading the reference

Instant.parse accepts ISO 8601 UTC text. atZone converts an instant to a regional representation without changing the instant. plusDays follows local calendar arithmetic, while plusHours follows elapsed time for ZonedDateTime. ZoneRules.getValidOffsets reveals zero, one or two valid offsets for a local date-time. Use explicit formatters and Locale rather than relying on machine defaults.

## Exercise 1: Preserve an instant across zones: predict an edited check

Task: Change Example A's assertion to `ny.toLocalDate().equals(java.time.LocalDate.of(2024, 12, 31));`, predict whether it holds, then run and restore it.

Changing the display zone does not move the event. A date-only grouping can nevertheless change because calendar boundaries differ by zone.

The unchanged code is the part that Example A adds:

```java
var instant = java.time.Instant.parse("2024-01-01T00:00:00Z");
var utc = instant.atZone(java.time.ZoneId.of("UTC"));
var ny = instant.atZone(java.time.ZoneId.of("America/New_York"));
assert utc.toInstant().equals(ny.toInstant()) &&
ny.toLocalDate().equals(java.time.LocalDate.of(2023, 12, 31));
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `utc.toInstant().equals(ny.toInstant()) && ny.toLocalDate().equals(java.time.LocalDate.of(2023, 12, 31))`.

**Verify:** Explain why the edited assertion is false for the values that satisfy `utc.toInstant().equals(ny.toInstant()) && ny.toLocalDate().equals(java.time.LocalDate.of(2023, 12, 31))`.

## Exercise 2: Compare calendar and elapsed days: debug a regression

Task: A regression in Example B's new code makes one line read `13,`. Repair it using the failing assertion.

A day in the local calendar crosses a daylight-saving gap here. Duration and calendar arithmetic answer different questions.

The unchanged code is the part that Example B adds:

```java
var start = java.time.ZonedDateTime.of(
  2024,
  3,
  9,
  12,
  0,
  0,
  0,
  java.time.ZoneId.of("America/New_York")
);
var nextDay = start.plusDays(1);
var next24 = start.plusHours(24);
assert java.time.Duration.between(start, nextDay).toHours() == 23;
assert nextDay.getHour() == 12 && next24.getHour() == 13;
```

**Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `nextDay.getHour() == 12 && next24.getHour() == 13`; the repaired line reads `12,`.

**Verify:** Explain how the changed token alters the value that `nextDay.getHour() == 12 && next24.getHour() == 13` tests.

## Exercise 3: Detect a nonexistent local time

Task: Ask for valid offsets at 2024-03-10 02:30 in New York.

A parser may resolve a gap according to an API policy, but the original local reading did not occur. Validate explicitly when silent adjustment is unacceptable.

```java
var zone = java.time.ZoneId.of("America/New_York");
var gap = java.time.LocalDateTime.of(2024, 3, 10, 2, 30);
assert zone.getRules().getValidOffsets(gap).isEmpty();
```

**Expected:** zero valid offsets.

**Verify:** Control: changing `var gap = java.time.LocalDateTime.of(2024, 3, 10, 2, 30);` to `var gap = java.time.LocalDateTime.of(2025, 3, 10, 2, 30);` must fail the assertion on `zone.getRules().getValidOffsets(gap).isEmpty()`.

## Exercise 4: Detect an ambiguous local time

Task: Ask for offsets at 2024-11-03 01:30 in New York.

The clock reading occurs twice during the fall transition. A domain record needs an offset or a declared ambiguity-resolution policy to identify one instant.

```java
var overlap = java.time.LocalDateTime.of(2024, 11, 3, 1, 30);
assert zone.getRules().getValidOffsets(overlap).size() == 2;
```

**Expected:** two valid offsets.

**Verify:** Control: changing `var overlap = java.time.LocalDateTime.of(2024, 11, 3, 1, 30);` to `var overlap = java.time.LocalDateTime.of(2025, 11, 3, 1, 30);` must fail the assertion on `zone.getRules().getValidOffsets(overlap).size() == 2`.

## Exercise 5: Parse a strict calendar date

Task: Parse 2024-02-29 and reject 2023-02-29 with ISO_LOCAL_DATE.

Validation follows calendar rules rather than accepting any numeric month/day combination. Keep parsing failures distinct from a missing date.

```java
assert java.time.LocalDate.parse("2024-02-29").getDayOfMonth() == 29;
boolean invalid = false;
try {
  java.time.LocalDate.parse("2023-02-29");
} catch (java.time.format.DateTimeParseException expected) {
  invalid = true;
}
assert invalid;
```

**Expected:** leap-day accepted only for 2024.

**Verify:** Control: changing `java.time.LocalDate.parse("2023-02-29");` to `java.time.LocalDate.parse("2024-02-29");` must fail the assertion on `invalid`.

## Exercise 6: Use a half-open time window

Task: Include an instant at the start and exclude an instant exactly at the end of a one-hour window.

Half-open intervals avoid double-counting an event on adjacent boundaries. The policy should be consistent across storage, queries and reports.

```java
var end = instant.plusSeconds(3600);
assert !instant.isBefore(instant) && instant.isBefore(end);
assert !(!end.isBefore(instant) && end.isBefore(end));
```

**Expected:** start included; end excluded.

**Verify:** Control: changing `assert !(!end.isBefore(instant) && end.isBefore(end));` to `assert !(!end.isBefore(instant) || end.isBefore(end));` inside the assertion must make it fail.

## After comparing the answer

Repeat Exercise 2 in your copy for the fall transition on 2024-11-02 and predict the elapsed hours between noon and the next day's noon (25).

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.
