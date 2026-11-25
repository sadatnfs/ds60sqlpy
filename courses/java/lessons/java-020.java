// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Find the first duplicate boundary: change one input
    // Change `int[] sorted = { 1, 2, 2, 5 };` to `int[] sorted = { 2, 2, 2, 5 };` in Example A
    // and predict which assertion fails and why.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `lowerBound(sorted, 2) == 1 && lowerBound(sorted, 6) == 4`.

    // Exercise 2: Handle empty and outside searches: diagnose an edited check
    // Example B's new assertion was edited to `assert lowerBound(new int[1], 7) == 0;`. Explain
    // why it fails for unchanged state and restore it.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `lowerBound(new int[0], 7) == 0`; the restored assertion passes.

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
