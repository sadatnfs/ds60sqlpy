// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Guard a nullable value: predict an edited check
    // Change Example A's assertion to `assert nonempty;`, predict whether it holds, then run and
    // restore it.
    // Expected: The edited run fails with an `AssertionError` from the assertion on `!nonempty`.

    // Exercise 2: Trace a prefix sum: debug a regression
    // A regression in Example B's new code makes one line read `sum -= values[i];`. Repair it
    // using the failing assertion.
    // Expected: The unrepaired run fails with an `AssertionError` from the assertion on
    // `prefixes.equals(List.of(2, 6, 12)) && sum == 12`; the repaired line reads `sum +=
    // values[i];`.

    // Exercise 3: Handle an empty loop
    // Run the same sum pattern over an empty int array.
    // Expected: sum 0 and zero iterations.

    // Exercise 4: Choose a value with a switch expression
    // Classify Saturday and Wednesday with one exhaustive switch expression over
    // java.time.DayOfWeek.
    // Expected: weekend, then weekday.

    // Exercise 5: Stop at the first match
    // Search 3, 8, 8 for the first 8 and stop immediately.
    // Expected: index 1.

    // Exercise 6: Expose a wrong boundary
    // Compare a loop using i <= length with the valid i < length contract on a one-element
    // array.
    // Expected: wrong loop raises ArrayIndexOutOfBoundsException.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
