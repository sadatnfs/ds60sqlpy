// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Test the pure calculation: change one input
    // Copy Example A into a scratch `Main.java` and change `total(0, 125);` to `total(1, 125);`.
    // Before running it with `java -ea Main`, predict which assertion fails and which value it
    // now sees; then run it and restore the original line.
    // Expected: The changed run fails with an `AssertionError` from the assertion on `invalid`.
    // Restoring the original line brings back the worked observation: 375 cents; nonpositive
    // quantity rejected.

    // Exercise 2: Compose a deterministic service: debug a regression
    // A regression changed one token in the code that Example B adds after Example A, so one
    // line now reads `id.equals("item-a") ? java.util.OptionalLong.of(126) :
    // java.util.OptionalLong.empty();`. Run Example B with that line, use the failing assertion
    // to locate the defect and repair it without changing the assertion.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `quote.totalCents() == 250 && quote.created().equals(instant) &&
    // audit.equals(List.of("quoted:item-a"))`; after it the line reads `id.equals("item-a") ?
    // java.util.OptionalLong.of(125) : java.util.OptionalLong.empty();` again and total 250,
    // time 2026-01-01T00:00:00Z, one audit event.

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
