# java-015: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

Time has several meanings. Instant identifies a point on the UTC timeline. LocalDate describes a calendar date without a time zone. LocalDateTime is a wall-clock reading that may be ambiguous or nonexistent in a region because of daylight-saving transitions. ZonedDateTime combines local fields with a zone and resolved offset. A calendar day is not always24 elapsed hours. Store the meaning required by the domain rather than treating every timestamp as interchangeable text. Parse explicit offsets for event instants, and use a region zone when calendar rules matter.

**Instant:** A point on the UTC timeline.

**Local date-time:** Calendar and clock fields without a resolved zone offset.

**Zone rule:** A region-specific mapping between local time and offsets.

## Reading the reference

Instant.parse acceptsISO8601UTCtext. atZone converts an instant to a regional representation without changing the instant. plusDays follows local calendar arithmetic,while plusHours follows elapsed time for ZonedDateTime. ZoneRules.getValidOffsets reveals zero,one or two valid offsets for a local date-time. Use explicit formatters and Locale rather than relying on machine defaults.

## Exercise 1: Preserve an instant across zones

Task: Parse `2024-01-01T00:00:00Z` and view it in UTC and America/New_York.

Changing the display zone does not move the event. A date-only grouping can nevertheless change because calendar boundaries differ by zone.

```java
var instant = java.time.Instant.parse("2024-01-01T00:00:00Z");
var utc = instant.atZone(java.time.ZoneId.of("UTC"));
var ny = instant.atZone(java.time.ZoneId.of("America/New_York"));
assert utc.toInstant().equals(ny.toInstant()) &&
ny.toLocalDate().equals(java.time.LocalDate.of(2023, 12, 31));
```

**Expected:** same instant; New York local date 2023-12-31.

**Verify:** Compare the program values or named exception with same instant; New York local date 2023-12-31. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Compare calendar and elapsed days

Task: Start at noon before the2024New York spring transition and compareplusDays1 withplusHours24.

A day in the local calendar crosses a daylight-saving gap here. Duration and calendar arithmetic answer different questions.

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

**Expected:** calendar next noon is23 elapsed hours later;24hours reaches13:00.

**Verify:** Compare the program values or named exception with calendar next noon is23 elapsed hours later;24hours reaches13:00. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Detect a nonexistent local time

Task: Ask for valid offsets at2024-03-10 02:30 in New York.

A parser may resolve a gap according to an API policy, but the original local reading did not occur. Validate explicitly when silent adjustment is unacceptable.

```java
var zone = java.time.ZoneId.of("America/New_York");
var gap = java.time.LocalDateTime.of(2024, 3, 10, 2, 30);
assert zone.getRules().getValidOffsets(gap).isEmpty();
```

**Expected:** zero valid offsets.

**Verify:** Compare the program values or named exception with zero valid offsets. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Detect an ambiguous local time

Task: Ask for offsets at2024-11-03 01:30 in New York.

The clock reading occurs twice during the fall transition. A domain record needs an offset or a declared ambiguity-resolution policy to identify one instant.

```java
var overlap = java.time.LocalDateTime.of(2024, 11, 3, 1, 30);
assert zone.getRules().getValidOffsets(overlap).size() == 2;
```

**Expected:** two valid offsets.

**Verify:** Compare the program values or named exception with two valid offsets. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

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

**Expected:** leap-day accepted only for2024.

**Verify:** Compare the program values or named exception with leap-day accepted only for2024. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Use a half-open time window

Task: Include an instant at the start and exclude an instant exactly at the end of a one-hour window.

Half-open intervals avoid double-counting an event on adjacent boundaries. The policy should be consistent across storage,queries and reports.

```java
var end = instant.plusSeconds(3600);
assert !instant.isBefore(instant) && instant.isBefore(end);
assert !(!end.isBefore(instant) && end.isBefore(end));
```

**Expected:** start included; end excluded.

**Verify:** Compare the program values or named exception with start included; end excluded. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
