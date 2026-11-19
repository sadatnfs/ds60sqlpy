// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Normalize at construction: change one input
    // Copy Example A into a scratch `Main.java` and change `Order order = new Order(" A ",
    // List.of("x"));` to `Order order = new Order(" A !", List.of("x"));`. Before running it
    // with `java -ea Main`, predict which assertion fails and which value it now sees; then run
    // it and restore the original line.
    // Expected: The changed run fails with an `AssertionError` from the assertion on
    // `order.id().equals("A") && order.items().equals(List.of("x"))`. Restoring the original
    // line brings back the worked observation: ID A and items[x].

    // Exercise 2: Copy caller-owned collections: debug a regression
    // A regression changed one token in the code that Example B adds after Example A, so one
    // line now reads `List<String> supplied = new ArrayList<>(List.of("x!"));`. Run Example B
    // with that line, use the failing assertion to locate the defect and repair it without
    // changing the assertion.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `copied.items().equals(List.of("x"))`; after it the line reads `List<String> supplied =
    // new ArrayList<>(List.of("x"));` again and record retains its original single item.

    // Exercise 3: Use value equality
    // Construct another Order with normalizedA and item x.
    // Expected: equals true and equal hashCode.

    // Exercise 4: Reject blank identity
    // Construct an Order with an all-space ID.
    // Expected: IllegalArgumentException.

    // Exercise 5: Protect the exposed collection
    // Attempt to add to order.items().
    // Expected: UnsupportedOperationException.

    // Exercise 6: Reject null collection members
    // Try creating an Order whose items contains null.
    // Expected: NullPointerException from the declared copy policy.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
