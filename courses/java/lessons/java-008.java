// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Normalize at construction
    // Create an Order with idspaceAspace and itemx.
    // Expected: idA and items[x].

    // Exercise 2: Copy caller-owned collections
    // Create an Order from a mutable list,then append to the original list.
    // Expected: record retains its original single item.

    // Exercise 3: Use value equality
    // Construct another Order with normalizedA and itemx.
    // Expected: equals true and equalhashCode.

    // Exercise 4: Reject blank identity
    // Construct an Order with an all-space ID.
    // Expected: IllegalArgumentException.

    // Exercise 5: Protect the exposed collection
    // Attempt to add toorder.items().
    // Expected: UnsupportedOperationException.

    // Exercise 6: Reject null collection members
    // Try creating an Order whose items containsnull.
    // Expected: NullPointerException from the declaredcopy policy.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
