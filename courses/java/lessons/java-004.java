// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Call a pure calculation: predict an edited check
    // Change Example A's assertion to `assert doubleValue(1) == 0;`, predict whether it holds,
    // then run and restore it.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `doubleValue(0) == 0`.

    // Exercise 2: Validate a precondition: debug a regression
    // A regression in Example B's new code makes one line read `positiveArea(1, 4);`. Repair it
    // using the failing assertion.
    // Expected: The unrepaired run fails with an `AssertionError` from the assertion on
    // `badArea`; the repaired line reads `positiveArea(0, 4);`.

    // Exercise 3: Observe copied primitive values
    // Pass int 5 to a helper that reassigns its local parameter to 99.
    // Expected: caller value remains 5.

    // Exercise 4: Observe shared object mutation
    // Pass a list containing 1 to a helper that appends 2.
    // Expected: caller list becomes 1, 2.

    // Exercise 5: Distinguish reference reassignment
    // Pass the list to a helper that replaces only its local parameter with a new list.
    // Expected: caller list remains 1, 2.

    // Exercise 6: Inspect overload selection
    // Call describe with int 1 and long 1L using two overloads.
    // Expected: int and long respectively.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
