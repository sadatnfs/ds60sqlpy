// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Print a first result: change one input
    // Copy Example A into a scratch `Main.java` and change `String message = "Hello, Java";` to
    // `String message = "Hello, Java!";`. Before running it with `java -ea Main`, predict which
    // assertion fails and which value it now sees; then run it and restore the original line.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `message.equals("Hello, Java")`. Restoring the original line brings back the worked
    // observation: one line Hello, Java.

    // Exercise 2: Evaluate before printing: diagnose an edited check
    // A careless edit changed the assertion that Example B adds after Example A so that it reads
    // `assert line.equals("total=6");`. Run Example B with that line, explain why the edited
    // assertion now fails for the same program state, and restore it.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `line.equals("total=5")`; after it the line reads `assert line.equals("total=5");` again
    // and integer 5 and text total=5.

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
