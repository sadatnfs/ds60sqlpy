// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Use independent table cases: change one input
    // Copy Example A into a scratch `Main.java` and change `int[][] cases = { { -2, 0 }, { 0, 0
    // }, { 3, 3 }, { 9, 5 } };` to `int[][] cases = { { -2, 1 }, { 0, 0 }, { 3, 3 }, { 9, 5 }
    // };`. Before running it with `java -ea Main`, predict which assertion fails and which value
    // it now sees; then run it and restore the original line.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `clamp(row[0], 0, 5) == row[1]`. Restoring the original line brings back the worked
    // observation: outputs 0, 0, 3, 5.

    // Exercise 2: Check a boundary failure: debug a regression
    // Introduce one deliberate defect into the code that Example B adds after Example A and
    // explain which observation exposes it, then repair it.
    // Expected: The defective copy changes the observation; the repaired copy reproduces the
    // worked observation: exception observed.

    // Exercise 3: Test an idempotence property
    // For values -10 through 10, clamping an already clamped value leaves it unchanged.
    // Expected: all 21 cases satisfy idempotence.

    // Exercise 4: Detect a broken implementation
    // Use a mutant that returns upper for values below lower and show the table rejects it.
    // Expected: at least one mismatch.

    // Exercise 5: Verify the exception checker itself
    // Ask the helper to expect an exception from a successful action and catch its
    // AssertionError.
    // Expected: checker fails when no exception is thrown.

    // Exercise 6: Test a fresh transfer property
    // Reverse arrays of length 0, 1, 3 twice using a separate copy and compare with originals.
    // Expected: all originals restored; input arrays unchanged.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
