# java-015: Dates, time zones and formatting

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-014`

## Learning objectives

Represent instants, local dates and zoned times correctly across daylight-saving gaps and overlaps.

The six exercises practice these steps:

- Preserve an instant across zones.
- Compare calendar and elapsed days.
- Detect a nonexistent local time.
- Detect an ambiguous local time.
- Parse a strict calendar date.
- Use a half-open time window.

## Purpose and mental model

Time has several meanings. Instant identifies a point on the UTC timeline. LocalDate describes a calendar date without a time zone. LocalDateTime is a wall-clock reading that may be ambiguous or nonexistent in a region because of daylight-saving transitions. ZonedDateTime combines local fields with a zone and resolved offset. A calendar day is not always 24 elapsed hours. Store the meaning required by the domain rather than treating every timestamp as interchangeable text. Parse explicit offsets for event instants, and use a region zone when calendar rules matter.

## Vocabulary and concepts

**Instant:** A point on the UTC timeline.

**Local date-time:** Calendar and clock fields without a resolved zone offset.

**Zone rule:** A region-specific mapping between local time and offsets.

## How to run this lesson

Every check uses fixed dates and the `America/New_York` zone, never the system clock, so results do not depend on where or when you run them; the zone rules come from the JDK's bundled time zone data.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

Instant.parse accepts ISO 8601 UTC text. atZone converts an instant to a regional representation without changing the instant. plusDays follows local calendar arithmetic, while plusHours follows elapsed time for ZonedDateTime. ZoneRules.getValidOffsets reveals zero, one or two valid offsets for a local date-time. Use explicit formatters and Locale rather than relying on machine defaults.

## Worked example / walkthrough

### Example A: Preserve an instant across zones

Changing the display zone does not move the event. A date-only grouping can nevertheless change because calendar boundaries differ by zone.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    var instant = java.time.Instant.parse("2024-01-01T00:00:00Z");
    var utc = instant.atZone(java.time.ZoneId.of("UTC"));
    var ny = instant.atZone(java.time.ZoneId.of("America/New_York"));
    assert utc.toInstant().equals(ny.toInstant()) &&
    ny.toLocalDate().equals(java.time.LocalDate.of(2023, 12, 31));
  }
}
```

**Expected:** same instant; New York local date 2023-12-31.

### Example B: Compare calendar and elapsed days

A day in the local calendar crosses a daylight-saving gap here. Duration and calendar arithmetic answer different questions.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    var instant = java.time.Instant.parse("2024-01-01T00:00:00Z");
    var utc = instant.atZone(java.time.ZoneId.of("UTC"));
    var ny = instant.atZone(java.time.ZoneId.of("America/New_York"));
    assert utc.toInstant().equals(ny.toInstant()) &&
    ny.toLocalDate().equals(java.time.LocalDate.of(2023, 12, 31));

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
  }
}
```

**Expected:** calendar next noon is 23 elapsed hours later; 24 hours reaches 13:00.

## Prediction before your attempt

Before running Example A, decide whether `2024-01-01T00:00:00Z` viewed in New York is the same instant and which calendar date it shows (2023-12-31, because New York is five hours behind UTC). For Example B, starting at noon on 2024-03-09 in New York, predict the hour after `plusDays(1)` and after `plusHours(24)`, and how many elapsed hours separate the start from the calendar next day. Then predict how many valid offsets 02:30 on 2024-03-10 has in New York.

## Exercises

1. **Preserve an instant across zones: predict an edited check.** Change Example A's assertion to `ny.toLocalDate().equals(java.time.LocalDate.of(2024, 12, 31));`, predict whether it holds, then run and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `utc.toInstant().equals(ny.toInstant()) && ny.toLocalDate().equals(java.time.LocalDate.of(2023, 12, 31))`.
   **Verify:** Explain why the edited assertion is false for the values that satisfy `utc.toInstant().equals(ny.toInstant()) && ny.toLocalDate().equals(java.time.LocalDate.of(2023, 12, 31))`.

2. **Compare calendar and elapsed days: debug a regression.** A regression in Example B's new code makes one line read `13,`. Repair it using the failing assertion.
   **Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `nextDay.getHour() == 12 && next24.getHour() == 13`; the repaired line reads `12,`.
   **Verify:** Explain how the changed token alters the value that `nextDay.getHour() == 12 && next24.getHour() == 13` tests.

3. **Detect a nonexistent local time.** Ask for valid offsets at 2024-03-10 02:30 in New York.
   **Expected:** zero valid offsets.
   **Verify:** Control: changing `var gap = java.time.LocalDateTime.of(2024, 3, 10, 2, 30);` to `var gap = java.time.LocalDateTime.of(2025, 3, 10, 2, 30);` must fail the assertion on `zone.getRules().getValidOffsets(gap).isEmpty()`.

4. **Detect an ambiguous local time.** Ask for offsets at 2024-11-03 01:30 in New York.
   **Expected:** two valid offsets.
   **Verify:** Control: changing `var overlap = java.time.LocalDateTime.of(2024, 11, 3, 1, 30);` to `var overlap = java.time.LocalDateTime.of(2025, 11, 3, 1, 30);` must fail the assertion on `zone.getRules().getValidOffsets(overlap).size() == 2`.

5. **Parse a strict calendar date.** Parse 2024-02-29 and reject 2023-02-29 with ISO_LOCAL_DATE.
   **Expected:** leap-day accepted only for 2024.
   **Verify:** Control: changing `java.time.LocalDate.parse("2023-02-29");` to `java.time.LocalDate.parse("2024-02-29");` must fail the assertion on `invalid`.

6. **Use a half-open time window.** Include an instant at the start and exclude an instant exactly at the end of a one-hour window.
   **Expected:** start included; end excluded.
   **Verify:** Control: changing `assert !(!end.isBefore(instant) && end.isBefore(end));` to `assert !(!end.isBefore(instant) || end.isBefore(end));` inside the assertion must make it fail.

## Common pitfalls and diagnosis

Storing a `LocalDateTime` for an event loses the information needed to find the instant, and in a daylight-saving gap or overlap the reading does not identify one instant at all. Adding 24 hours is not the same as adding one day across a transition. Parsing text with a zone-less pattern and then attaching the system default zone makes results depend on the machine. Closed windows that include both endpoints count an event at the boundary twice when windows are adjacent.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First note that the edit changes the expected date to 2024-12-31 while the instant stays the same. Then convert the instant to New York local time and write its date. Finally, compare the two dates and decide whether the clock or the claim changed.
- **Exercise 2:** First notice that the edit moves the start to 13:00 on 2024-03-09. Then compute the hour after `plusDays(1)` and after `plusHours(24)` from that start. Finally, compare them with 12 and 13 and explain why the elapsed-hours assertion still passes.
- **Exercise 3:** First build `LocalDateTime.of(2024, 3, 10, 2, 30)`. Then ask the zone rules for its valid offsets in New York. Finally, explain why the list is empty: the clocks jump from 02:00 straight to 03:00 that night.
- **Exercise 4:** First build `LocalDateTime.of(2024, 11, 3, 1, 30)`. Then ask the zone rules for its valid offsets. Finally, explain why there are two, one before and one after the clocks move back.
- **Exercise 5:** First parse "2024-02-29" with `LocalDate.parse`. Then parse "2023-02-29" inside a `try` block and catch `DateTimeParseException`. Finally, explain which calendar rule separates the two years.
- **Exercise 6:** First define the window as `[instant, instant + 3600 seconds)`, with the start included and the end excluded. Then test the start and the end with `!x.isBefore(start) && x.isBefore(end)`. Finally, explain why two adjacent windows never count the same instant.

## Self-check and retrieval

Without the guide, explain the difference between `Instant`, `LocalDate`, `LocalDateTime` and `ZonedDateTime`, and which one you would store for a meeting, a birthday and a log event. Then explain why the March day in New York lasts 23 hours and what zero or two valid offsets mean for a local time.

## Next step

Continue with `java-016`: Files, paths and character encoding. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/time/ZonedDateTime.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-015: Dates, time zones and formatting.
Read courses/java/guides/java-015.md and courses/java/lessons/java-015.java. Direct prerequisites: `java-014`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
