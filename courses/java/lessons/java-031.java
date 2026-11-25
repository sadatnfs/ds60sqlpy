// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Inspect a retained annotation: predict an edited check
    // Change Example A's assertion to `assert version != null && version.value() == 3;`, predict
    // whether it holds, then run and restore it.
    // Expected: The edited run fails with an `AssertionError` from the assertion on `version !=
    // null && version.value() == 2`.

    // Exercise 2: Invoke a known public method reflectively: diagnose an edited check
    // Example B's new assertion was edited to `assert method.invoke(new Friendly(),
    // "Ada!").equals("Hello, Ada");`. Explain why it fails for unchanged state and restore it.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `method.invoke(new Friendly(), "Ada").equals("Hello, Ada")`; the restored assertion
    // passes.

    // Exercise 3: Load a real local service descriptor
    // Create the temporaryMETA-INF/services entry and discover Greeting providers.
    // Expected: one Friendly provider with version 2 and working greet.

    // Exercise 4: Preserve a reflected target failure
    // Invoke greet with blank text and inspect InvocationTargetException cause.
    // Expected: cause IllegalArgumentException.

    // Exercise 5: Reject missing class and method contracts
    // Look up an absent class and an unsupported greet(int) signature.
    // Expected: ClassNotFoundException and NoSuchMethodException.

    // Exercise 6: Treat provider metadata as a policy input
    // Accept provider versions 1..2 and reject a hypothetical version 3 under the current
    // consumer contract.
    // Expected: version 2 accepted; version 3 rejected.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
