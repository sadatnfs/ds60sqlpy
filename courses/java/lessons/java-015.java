// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Preserve an instant across zones
    // Parse2024-01-01T00:00:00Z and view it inUTC andAmerica/New_York.
    // Expected: same instant;New York local date2023-12-31.

    // Exercise 2: Compare calendar and elapsed days
    // Start at noon before the2024New York spring transition and compareplusDays1
    // withplusHours24.
    // Expected: calendar next noon is23 elapsed hours later;24hours reaches13:00.

    // Exercise 3: Detect a nonexistent local time
    // Ask for valid offsets at2024-03-10 02:30 inNew York.
    // Expected: zero valid offsets.

    // Exercise 4: Detect an ambiguous local time
    // Ask for offsets at2024-11-03 01:30 inNew York.
    // Expected: two valid offsets.

    // Exercise 5: Parse a strict calendar date
    // Parse2024-02-29 and reject2023-02-29 withISO_LOCAL_DATE.
    // Expected: leap-day accepted only for2024.

    // Exercise 6: Use a half-open time window
    // Include an instant at the start and exclude an instant exactly at the end of a one-hour
    // window.
    // Expected: start included;end excluded.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
