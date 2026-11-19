// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Filter and sum: change one input
    // Copy Example A into a scratch `Main.java` and change `int total = List.of(1, 2, 3, 4)` to
    // `int total = List.of(2, 2, 3, 4)`. Before running it with `java -ea Main`, predict which
    // assertion fails and which value it now sees; then run it and restore the original line.
    // Expected: The changed run fails with an `AssertionError` from the assertion on `total ==
    // 20`. Restoring the original line brings back the worked observation: 20.

    // Exercise 2: Observe laziness with an explicit terminal: debug a regression
    // A regression changed one token in the code that Example B adds after Example A, so one
    // line now reads `return value + 2;`. Run Example B with that line, use the failing
    // assertion to locate the defect and repair it without changing the assertion.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `pipeline.toList().equals(List.of(2, 4, 6)) && calls.get() == 3`; after it the line reads
    // `return value * 2;` again and counter 0 before terminal and 3 after.

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
