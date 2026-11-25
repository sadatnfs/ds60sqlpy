// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Represent a missing lookup: change one input
    // Change `Map<String, Integer> data = Map.of("a", 7);` to `Map<String, Integer> data =
    // Map.of("a", 8);` in Example A and predict which assertion fails and why.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `known.orElseThrow() == 7 && missing.isEmpty()`.

    // Exercise 2: Transform only present values: diagnose an edited check
    // Example B's new assertion was edited to `assert known.map(value -> value +
    // 2).orElseThrow() == 14;`. Explain why it fails for unchanged state and restore it.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `known.map(value -> value * 2).orElseThrow() == 14`; the restored assertion passes.

    // Exercise 3: Compare eager and lazy fallback
    // Use a counter-producing fallback with orElse and orElseGet on a present value.
    // Expected: orElse increments; orElseGet does not.

    // Exercise 4: Reject malformed lookup input
    // Validate an empty identifier before consulting the map.
    // Expected: IllegalArgumentException rather than empty.

    // Exercise 5: Flatten a nullable transformation
    // Parse an optional numeric string through a helper returning Optional<Integer>.
    // Expected: valid 12 present; bad text empty under this declared parser policy.

    // Exercise 6: Expose unsafe get
    // Call get on empty and catchNoSuchElementException.
    // Expected: specific absence failure.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
