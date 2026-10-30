// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Use independent table cases
    // Test clamp for values -2,0,3,9 under bounds 0..5.
    // Expected: outputs 0,0,3,5.

    // Exercise 2: Check a boundary failure
    // Callclamp withlower5,upper2 and requireIllegalArgumentException.
    // Expected: exception observed.

    // Exercise 3: Test an idempotence property
    // For values-10 through10,clamping an already clamped value leaves it unchanged.
    // Expected: all21 cases satisfyidempotence.

    // Exercise 4: Detect a broken implementation
    // Use a mutant that returns upper for values below lower and show the table rejects it.
    // Expected: at least one mismatch.

    // Exercise 5: Verify the exception checker itself
    // Ask the helper to expect an exception from a successful action and catch
    // itsAssertionError.
    // Expected: checker fails when no exception is thrown.

    // Exercise 6: Test a fresh transfer property
    // Reverse arrays oflength0,1,3 twice using a separate copy and compare with originals.
    // Expected: all originals restored; input arrays unchanged.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
