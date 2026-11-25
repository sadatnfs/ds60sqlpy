// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Filter and sum: change one input
    // Change `int total = List.of(1, 2, 3, 4)` to `int total = List.of(2, 2, 3, 4)` in Example A
    // and predict which assertion fails and why.
    // Expected: The edited run fails with an `AssertionError` from the assertion on `total ==
    // 20`.

    // Exercise 2: Observe laziness with an explicit terminal: debug a regression
    // A regression in Example B's new code makes one line read `return value + 2;`. Repair it
    // using the failing assertion.
    // Expected: The unrepaired run fails with an `AssertionError` from the assertion on
    // `pipeline.toList().equals(List.of(2, 4, 6)) && calls.get() == 3`; the repaired line reads
    // `return value * 2;`.

    // Exercise 3: Group with a collector
    // Count red, blue, red with groupingBy and counting.
    // Expected: red 2L, blue 1L.

    // Exercise 4: Reject stream reuse
    // Consume a stream once, then attempt another terminal operation.
    // Expected: IllegalStateException.

    // Exercise 5: Check the reduction identity
    // Compare sum reduction with identity 0 against a deliberately wrong identity 10.
    // Expected: correct 6; wrong 16 in the sequential fixture.

    // Exercise 6: Expose nonassociative subtraction
    // Compare (10-3)-2 with 10-(3-2), then use an associative sum for a parallel fixture.
    // Expected: 5 versus 9; parallel sum 5050.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
