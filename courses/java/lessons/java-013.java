// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Use a predicate: predict an edited check
    // Copy Example A into a scratch `Main.java` and change `assert positive.test(3) &&
    // !positive.test(0) && !positive.test(-1);` to `assert positive.test(3) && !positive.test(1)
    // && !positive.test(-1);` inside its assertion. Before running it with `java -ea Main`,
    // predict whether the assertion still holds and explain why; then restore it.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `positive.test(3) && !positive.test(0) && !positive.test(-1)`. Restoring the original line
    // brings back the worked observation: true, false, false.

    // Exercise 2: Compose transformations: diagnose an edited check
    // A careless edit changed the assertion that Example B adds after Example A so that it reads
    // `assert strip.andThen(upper).apply(" red !").equals("RED");`. Run Example B with that
    // line, explain why the edited assertion now fails for the same program state, and restore
    // it.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `strip.andThen(upper).apply(" red ").equals("RED")`; after it the line reads `assert
    // strip.andThen(upper).apply(" red ").equals("RED");` again and input space red space
    // becomes RED.

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
