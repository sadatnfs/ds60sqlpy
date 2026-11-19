// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Find the first duplicate boundary: change one input
    // Copy Example A into a scratch `Main.java` and change `int[] sorted = { 1, 2, 2, 5 };` to
    // `int[] sorted = { 2, 2, 2, 5 };`. Before running it with `java -ea Main`, predict which
    // assertion fails and which value it now sees; then run it and restore the original line.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `lowerBound(sorted, 2) == 1 && lowerBound(sorted, 6) == 4`. Restoring the original line
    // brings back the worked observation: indices 1 and 4.

    // Exercise 2: Handle empty and outside searches: diagnose an edited check
    // A careless edit changed the assertion that Example B adds after Example A so that it reads
    // `assert lowerBound(new int[1], 7) == 0;`. Run Example B with that line, explain why the
    // edited assertion now fails for the same program state, and restore it.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `lowerBound(new int[0], 7) == 0`; after it the line reads `assert lowerBound(new int[0],
    // 7) == 0;` again and both return 0.

    // Exercise 3: Preserve stable ties
    // Sort records (a, 2), (b, 1) and (c, 2) by key only and inspect the equal-key order.
    // Expected: IDs b, a, c.

    // Exercise 4: Solve a greedy counterexample
    // Find minimum coins for amount 6 using coins 1, 3, 4.
    // Expected: 2 coins, using 3+3 rather than 4+1+1.

    // Exercise 5: Represent an unreachable amount
    // Solve amount 3 with only coin 2 and amount 0 with any positive coins.
    // Expected: -1 for unreachable amount 3; 0 for amount 0.

    // Exercise 6: Reject invalid recurrence inputs
    // Pass a negative amount or a zero-valued coin.
    // Expected: IllegalArgumentException for both.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
