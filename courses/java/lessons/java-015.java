// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Preserve an instant across zones: predict an edited check
    // Change Example A's assertion to `ny.toLocalDate().equals(java.time.LocalDate.of(2024, 12,
    // 31));`, predict whether it holds, then run and restore it.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `utc.toInstant().equals(ny.toInstant()) &&
    // ny.toLocalDate().equals(java.time.LocalDate.of(2023, 12, 31))`.

    // Exercise 2: Compare calendar and elapsed days: debug a regression
    // A regression in Example B's new code makes one line read `13,`. Repair it using the
    // failing assertion.
    // Expected: The unrepaired run fails with an `AssertionError` from the assertion on
    // `nextDay.getHour() == 12 && next24.getHour() == 13`; the repaired line reads `12,`.

    // Exercise 3: Detect a nonexistent local time
    // Ask for valid offsets at 2024-03-10 02:30 in New York.
    // Expected: zero valid offsets.

    // Exercise 4: Detect an ambiguous local time
    // Ask for offsets at 2024-11-03 01:30 in New York.
    // Expected: two valid offsets.

    // Exercise 5: Parse a strict calendar date
    // Parse 2024-02-29 and reject 2023-02-29 with ISO_LOCAL_DATE.
    // Expected: leap-day accepted only for 2024.

    // Exercise 6: Use a half-open time window
    // Include an instant at the start and exclude an instant exactly at the end of a one-hour
    // window.
    // Expected: start included; end excluded.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
