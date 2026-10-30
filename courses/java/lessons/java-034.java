// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Test the pure calculation
    // Compute 3 items at 125 cents and check the zero/negative quantity policy.
    // Expected: 375 cents; nonpositive quantity rejected.

    // Exercise 2: Compose a deterministic service
    // Inject a fixedcatalog,clock and audit list,and request twoitems.
    // Expected: total250,time2026-01-01T00:00:00Z,oneauditevent.

    // Exercise 3: Reject an unknown catalog item
    // Requestmissing andinspecttheauditlist.
    // Expected: NoSuchElementException;no additional audit.

    // Exercise 4: Propagate an infrastructure failure
    // Inject a Catalog thatthrowsIOException.
    // Expected: same failure type;no success audit.

    // Exercise 5: Prove invalid quantity fails before a repository call
    // Use a countingcatalog and request negative quantity.
    // Expected: repositorycallcount0.

    // Exercise 6: Detect arithmetic overflow without an event
    // UseLong.MAX_VALUEunitprice andquantity2.
    // Expected: ArithmeticException;audit sink unused.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
