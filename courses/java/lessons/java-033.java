// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Read an admitted owned file
    // Create `input.txt` inside an owned root and read at most 10 bytes.
    // Expected: content hello.

    // Exercise 2: Reject lexical traversal and absolute paths
    // Attempt../outside.txt andanabsolutechildpath.
    // Expected: SecurityException for both.

    // Exercise 3: Enforce the byte limit after reading a bounded amount
    // Writefivebytes and request a four-byte maximum.
    // Expected: IOException for oversized content.

    // Exercise 4: Reject symbolic-link access under the declared policy
    // Create a link inside the owned root to another owned file and attempt to read throughit.
    // Expected: link rejected when platform supports creation;unsupported capability recorded explicitly.

    // Exercise 5: Keep operation names out of code execution
    // Admitonlyread_fixture andrejectrun_shell.
    // Expected: unknownoperationIllegalArgumentException.

    // Exercise 6: Build a restricted diagnostic record
    // Copy onlyrequest_id,operation and status from a map containing token andsource_text.
    // Expected: diagnostic excludes both sensitive fields.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
