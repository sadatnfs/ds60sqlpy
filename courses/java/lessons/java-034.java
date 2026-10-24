// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Test the pure calculation
    // Compute3items at125cents andcheckzero/negativequantity policy.
    // Expected: 375cents;nonpositivequantityrejected.

    // Exercise 2: Compose a deterministic service
    // Inject a fixedcatalog,clock andauditlist,andrequest twoitems.
    // Expected: total250,time2026-01-01T00:00:00Z,oneauditevent.

    // Exercise 3: Reject an unknown catalog item
    // Requestmissing andinspecttheauditlist.
    // Expected: NoSuchElementException;noadditionalaudit.

    // Exercise 4: Propagate an infrastructure failure
    // Inject aCatalog thatthrowsIOException.
    // Expected: samefailuretype;nosuccessaudit.

    // Exercise 5: Prove invalid quantity fails before a repository call
    // Use a countingcatalog andrequestnegativequantity.
    // Expected: repositorycallcount0.

    // Exercise 6: Detect arithmetic overflow without an event
    // UseLong.MAX_VALUEunitprice andquantity2.
    // Expected: ArithmeticException;auditsinkunused.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
