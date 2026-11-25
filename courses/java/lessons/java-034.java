// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Test the pure calculation: change one input
    // Change `total(0, 125);` to `total(1, 125);` in Example A and predict which assertion fails
    // and why.
    // Expected: The edited run fails with an `AssertionError` from the assertion on `invalid`.

    // Exercise 2: Compose a deterministic service: debug a regression
    // A regression in Example B's new code makes one line read `id.equals("item-a") ?
    // java.util.OptionalLong.of(126) : java.util.OptionalLong.empty();`. Repair it using the
    // failing assertion.
    // Expected: The unrepaired run fails with an `AssertionError` from the assertion on
    // `quote.totalCents() == 250 && quote.created().equals(instant) &&
    // audit.equals(List.of("quoted:item-a"))`; the repaired line reads `id.equals("item-a") ?
    // java.util.OptionalLong.of(125) : java.util.OptionalLong.empty();`.

    // Exercise 3: Reject an unknown catalog item
    // Request missing and inspect the audit list.
    // Expected: NoSuchElementException; no additional audit.

    // Exercise 4: Propagate an infrastructure failure
    // Inject a Catalog thatthrowsIOException.
    // Expected: same failure type; no success audit.

    // Exercise 5: Prove invalid quantity fails before a repository call
    // Use a counting catalog and request negative quantity.
    // Expected: repository call count 0.

    // Exercise 6: Detect arithmetic overflow without an event
    // Use a Long.MAX_VALUE unit price and quantity 2.
    // Expected: ArithmeticException; audit sink unused.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
