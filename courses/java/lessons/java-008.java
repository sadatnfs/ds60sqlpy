// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Normalize at construction: change one input
    // Change `Order order = new Order(" A ", List.of("x"));` to `Order order = new Order(" A !",
    // List.of("x"));` in Example A and predict which assertion fails and why.
    // Expected: The edited run fails with an `AssertionError` from the assertion on
    // `order.id().equals("A") && order.items().equals(List.of("x"))`.

    // Exercise 2: Copy caller-owned collections: debug a regression
    // A regression in Example B's new code makes one line read `List<String> supplied = new
    // ArrayList<>(List.of("x!"));`. Repair it using the failing assertion.
    // Expected: The unrepaired run fails with an `AssertionError` from the assertion on
    // `copied.items().equals(List.of("x"))`; the repaired line reads `List<String> supplied =
    // new ArrayList<>(List.of("x"));`.

    // Exercise 3: Use value equality
    // Construct another Order with normalized A and item x.
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
