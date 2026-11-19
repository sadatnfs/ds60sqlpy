// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Read from a producer: predict an edited check
    // Copy Example A into a scratch `Main.java` and change `assert sum(List.of(1, 2, 3)) ==
    // 6.0;` to `assert sum(List.of(2, 2, 3)) == 6.0;` inside its assertion. Before running it
    // with `java -ea Main`, predict whether the assertion still holds and explain why; then
    // restore it.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `sum(List.of(1, 2, 3)) == 6.0`. Restoring the original line brings back the worked
    // observation: sums 6.0 and 4.0.

    // Exercise 2: Write to a consumer: diagnose an edited check
    // A careless edit changed the assertion that Example B adds after Example A so that it reads
    // `assert numbers.equals(List.of(2, 2));`. Run Example B with that line, explain why the
    // edited assertion now fails for the same program state, and restore it.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `numbers.equals(List.of(1, 2))`; after it the line reads `assert numbers.equals(List.of(1,
    // 2));` again and list contains 1, 2.

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
