// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Use a predicate: predict an edited check
    // Change Example A's assertion to `assert positive.test(3) && !positive.test(1) &&
    // !positive.test(-1);`, predict whether it holds, then run and restore it.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `positive.test(3) && !positive.test(0) && !positive.test(-1)`.

    // Exercise 2: Compose transformations: diagnose an edited check
    // Example B's new assertion was edited to `assert strip.andThen(upper).apply(" red
    // !").equals("RED");`. Explain why it fails for unchanged state and restore it.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `strip.andThen(upper).apply(" red ").equals("RED")`; the restored assertion passes.

    // Exercise 3: Distinguish composition order
    // Compose add 1 and multiply 2 using andThen and compose on 3.
    // Expected: andThen gives 8; compose 7.

    // Exercise 4: Capture a stable threshold
    // Capture local threshold 10 in a predicate and test 9, 10, 11.
    // Expected: false, true, true under>=.

    // Exercise 5: Expose mutable captured state
    // Capture a list in a Consumer and append two values.
    // Expected: captured list becomes a, b.

    // Exercise 6: Use a named function for a contract
    // Pass a method reference to a parser that rejects blank input and parses a positive
    // integer.
    // Expected: 7 accepted; blank rejected.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
