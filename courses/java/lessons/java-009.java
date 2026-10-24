// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Close on normal completion
    // Open a Probe resource,recordbody,then inspect closure order.
    // Expected: eventsbody,closeA.

    // Exercise 2: Close in reverse order
    // Declare resourcesA thenB and leave the block.
    // Expected: closeB beforecloseA.

    // Exercise 3: Close after body failure
    // ThrowIllegalStateException in the body and inspect events after catching it.
    // Expected: closeA stillrecorded.

    // Exercise 4: Preserve suppressed close failure
    // Make the body throw and the resource close throw too.
    // Expected: primary messagebody;one suppressed exceptioncloseA.

    // Exercise 5: Observe close-only failure
    // Let the body succeed butclose throwIOException.
    // Expected: IOExceptioncloseA is primary.

    // Exercise 6: Retain a translated cause
    // Wrap anIOException inIllegalStateException with a domain message and inspectcause.
    // Expected: cause remains the originalIOException.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
