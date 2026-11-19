// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Call a pure calculation: predict an edited check
    // Copy Example A into a scratch `Main.java` and change `assert doubleValue(0) == 0;` to
    // `assert doubleValue(1) == 0;` inside its assertion. Before running it with `java -ea
    // Main`, predict whether the assertion still holds and explain why; then restore it.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `doubleValue(0) == 0`. Restoring the original line brings back the worked observation: 14
    // and 0.

    // Exercise 2: Validate a precondition: debug a regression
    // A regression changed one token in the code that Example B adds after Example A, so one
    // line now reads `positiveArea(1, 4);`. Run Example B with that line, use the failing
    // assertion to locate the defect and repair it without changing the assertion.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `badArea`; after it the line reads `positiveArea(0, 4);` again and 3 by 4 gives 12; zero
    // width throws IllegalArgumentException.

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
