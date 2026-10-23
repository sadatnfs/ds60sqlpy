# java-015: Dates, time zones and formatting

## Level and prerequisites

Intermediate, approximately 90 minutes. Direct prerequisites: `java-014`

## Learning objectives

Explain instant, local date-time, zone rule using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. The first investigation is Parse2024-01-01T00:00:00Z and view it inUTC andAmerica/New_York. The final exercise transfers the mechanism to use a half-open time window.

## Purpose and mental model

Time has several meanings. Instant identifies a point on theUTCtimeline. LocalDate describes a calendar date without a time zone. LocalDateTime is a wall-clock reading that may be ambiguous or nonexistent in a region because of daylight-saving transitions. ZonedDateTime combines local fields with a zone and resolved offset. A calendar day is not always24 elapsed hours. Store the meaning required by the domain rather than treating every timestamp as interchangeable text. Parse explicit offsets for event instants, and use a region zone when calendar rules matter.

## Vocabulary and concepts

**Instant:** A point on theUTCtimeline.

**Local date-time:** Calendar and clock fields without a resolved zone offset.

**Zone rule:** A region-specific mapping between local time and offsets.

## How to run this lesson

Open the Docker classroom, choose the prepared Java21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/java-015/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.



## Syntax anatomy and execution trace

Instant.parse acceptsISO8601UTCtext. atZone converts an instant to a regional representation without changing the instant. plusDays follows local calendar arithmetic,while plusHours follows elapsed time forZonedDateTime. ZoneRules.getValidOffsets reveals zero,one or two valid offsets for a local date-time. Use explicit formatters andLocale rather than relying on machine defaults.

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
        assert utc.toInstant().equals(ny.toInstant()) && ny.toLocalDate().equals(java.time.LocalDate.of(2023,12,31));
    }
}

```

**Expected:** same instant;New York local date2023-12-31.

### Example B: Compare calendar and elapsed days

A day in the local calendar crosses a daylight-saving gap here. Duration and calendar arithmetic answer different questions.

```java
import java.util.*;

public class Main {

    public static void main(String[] args) throws Exception {
        var instant = java.time.Instant.parse("2024-01-01T00:00:00Z");
        var utc = instant.atZone(java.time.ZoneId.of("UTC"));
        var ny = instant.atZone(java.time.ZoneId.of("America/New_York"));
        assert utc.toInstant().equals(ny.toInstant()) && ny.toLocalDate().equals(java.time.LocalDate.of(2023,12,31));

        var start = java.time.ZonedDateTime.of(2024,3,9,12,0,0,0,java.time.ZoneId.of("America/New_York"));
        var nextDay = start.plusDays(1); var next24 = start.plusHours(24);
        assert java.time.Duration.between(start,nextDay).toHours() == 23;
        assert nextDay.getHour() == 12 && next24.getHour() == 13;
    }
}

```

**Expected:** calendar next noon is23 elapsed hours later;24hours reaches13:00.

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

1. **Preserve an instant across zones.** Parse2024-01-01T00:00:00Z and view it inUTC andAmerica/New_York.
   **Expected:** same instant;New York local date2023-12-31.
   **Verify:** Compare your assertion values or captured diagnostic with same instant;New York local date2023-12-31.

2. **Compare calendar and elapsed days.** Start at noon before the2024New York spring transition and compareplusDays1 withplusHours24.
   **Expected:** calendar next noon is23 elapsed hours later;24hours reaches13:00.
   **Verify:** Compare your assertion values or captured diagnostic with calendar next noon is23 elapsed hours later;24hours reaches13:00.

3. **Detect a nonexistent local time.** Ask for valid offsets at2024-03-10 02:30 inNew York.
   **Expected:** zero valid offsets.
   **Verify:** Compare your assertion values or captured diagnostic with zero valid offsets.

4. **Detect an ambiguous local time.** Ask for offsets at2024-11-03 01:30 inNew York.
   **Expected:** two valid offsets.
   **Verify:** Compare your assertion values or captured diagnostic with two valid offsets.

5. **Parse a strict calendar date.** Parse2024-02-29 and reject2023-02-29 withISO_LOCAL_DATE.
   **Expected:** leap-day accepted only for2024.
   **Verify:** Compare your assertion values or captured diagnostic with leap-day accepted only for2024.

6. **Use a half-open time window.** Include an instant at the start and exclude an instant exactly at the end of a one-hour window.
   **Expected:** start included;end excluded.
   **Verify:** Compare your assertion values or captured diagnostic with start included;end excluded.

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

First reconstruct the values and identities in the worked example. Next isolate the line that changes the result when one input is altered. Finally compare the normal and failure paths with the stated contract. Use a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

## Self-check and retrieval

Close the solution and explain Instant, Local date-time, Zone rule in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/time/ZonedDateTime.html), reviewed2026-10-22. Examples and exercise fixtures are original course material. Consult `docs/implementation/java-content-status.md` for the actual compile/run receipts. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning for java-015: Dates, time zones and formatting.
Read courses/java/guides/java-015.md and courses/java/lessons/java-015.java. Direct prerequisites: `java-014`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```
