// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Print a first result: change one input
    // Change `String message = "Hello, Java";` to `String message = "Hello, Java!";` in Example
    // A and predict which assertion fails and why.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `message.equals("Hello, Java")`.

    // Exercise 2: Evaluate before printing: diagnose an edited check
    // Example B's new assertion was edited to `assert line.equals("total=6");`. Explain why it
    // fails for unchanged state and restore it.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `line.equals("total=5")`; the restored assertion passes.

    // Exercise 3: Trace sequential state
    // Start count 1, increment it, then multiply it by 3.
    // Expected: final count 6.

    // Exercise 4: Verify assertion mode
    // Use an assertion side effect only to detect whether this teaching launch enabled
    // assertions; fail explicitly otherwise.
    // Expected: assertion-enabled flag true.

    // Exercise 5: Separate runtime failure
    // Divide an integer by a variable containing 0 and catch exactly ArithmeticException.
    // Expected: ArithmeticException observed; program continues after the catch.

    // Exercise 6: Observe a real compiler diagnostic
    // Compile a small in-memory Broken class whose return statement lacks a semicolon; capture
    // diagnostics without executing it.
    // Expected: compiler result false and at least one ERROR diagnostic.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
