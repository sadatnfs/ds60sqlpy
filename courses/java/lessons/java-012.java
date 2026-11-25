// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Read from a producer: predict an edited check
    // Change Example A's assertion to `assert sum(List.of(2, 2, 3)) == 6.0;`, predict whether it
    // holds, then run and restore it.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `sum(List.of(1, 2, 3)) == 6.0`.

    // Exercise 2: Write to a consumer: diagnose an edited check
    // Example B's new assertion was edited to `assert numbers.equals(List.of(2, 2));`. Explain
    // why it fails for unchanged state and restore it.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `numbers.equals(List.of(1, 2))`; the restored assertion passes.

    // Exercise 3: Connect source and destination types
    // Copy List<Integer> into List<Number> with a bounded generic method.
    // Expected: destination contains 3, 4.

    // Exercise 4: Preserve generic return type
    // Call first on a String list and assign it directly to a String.
    // Expected: result alpha.

    // Exercise 5: Handle an empty input contract
    // Call first on an empty list and require a named failure.
    // Expected: NoSuchElementException.

    // Exercise 6: Observe erasure carefully
    // Compare runtime classes of ArrayList<String> and ArrayList<Integer>;explain why this does
    // not permit unsafe assignments.
    // Expected: runtime classes equal; compile-time contracts remain distinct.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
