// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Preserve an instant across zones: predict an edited check
    // Copy Example A into a scratch `Main.java` and change
    // `ny.toLocalDate().equals(java.time.LocalDate.of(2023, 12, 31));` to
    // `ny.toLocalDate().equals(java.time.LocalDate.of(2024, 12, 31));` inside its assertion.
    // Before running it with `java -ea Main`, predict whether the assertion still holds and
    // explain why; then restore it.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `utc.toInstant().equals(ny.toInstant()) &&
    // ny.toLocalDate().equals(java.time.LocalDate.of(2023, 12, 31))`. Restoring the original
    // line brings back the worked observation: same instant; New York local date 2023-12-31.

    // Exercise 2: Compare calendar and elapsed days: debug a regression
    // A regression changed one token in the code that Example B adds after Example A, so one
    // line now reads `13,`. Run Example B with that line, use the failing assertion to locate
    // the defect and repair it without changing the assertion.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `nextDay.getHour() == 12 && next24.getHour() == 13`; after it the line reads `12,` again
    // and calendar next noon is 23 elapsed hours later; 24 hours reaches 13:00.

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
