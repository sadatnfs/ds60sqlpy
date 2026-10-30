// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Close on normal completion
    // Open a Probe resource, record body, then inspect closure order.
    // Expected: events body, close A.

    // Exercise 2: Close in reverse order
    // Declare resourcesA thenB and leave the block.
    // Expected: closeB beforecloseA.

    // Exercise 3: Close after body failure
    // Throw IllegalStateException in the body and inspect events after catching it.
    // Expected: close A still recorded.

    // Exercise 4: Preserve suppressed close failure
    // Make the body throw and the resource close throw too.
    // Expected: primary message body;one suppressed exceptioncloseA.

    // Exercise 5: Observe close-only failure
    // Let the body succeed but close throwIOException.
    // Expected: IOExceptioncloseA is primary.

    // Exercise 6: Retain a translated cause
    // Wrap an IOException in IllegalStateException with a domain message and inspect cause.
    // Expected: cause remains the original IOException.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
