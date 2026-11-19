// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Represent a missing lookup: change one input
    // Copy Example A into a scratch `Main.java` and change `Map<String, Integer> data =
    // Map.of("a", 7);` to `Map<String, Integer> data = Map.of("a", 8);`. Before running it with
    // `java -ea Main`, predict which assertion fails and which value it now sees; then run it
    // and restore the original line.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `known.orElseThrow() == 7 && missing.isEmpty()`. Restoring the original line brings back
    // the worked observation: a present with 7; b empty.

    // Exercise 2: Transform only present values: diagnose an edited check
    // A careless edit changed the assertion that Example B adds after Example A so that it reads
    // `assert known.map(value -> value + 2).orElseThrow() == 14;`. Run Example B with that line,
    // explain why the edited assertion now fails for the same program state, and restore it.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `known.map(value -> value * 2).orElseThrow() == 14`; after it the line reads `assert
    // known.map(value -> value * 2).orElseThrow() == 14;` again and 14 and empty.

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
