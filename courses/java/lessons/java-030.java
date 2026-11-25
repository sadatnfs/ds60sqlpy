// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Round-trip version 2 data: change one input
    // Rebuild Example A from memory and propose one input change that makes the assertion on
    // `decode(encoded).equals(record)` fail.
    // Expected: The rebuild passes and the changed copy fails as predicted.

    // Exercise 2: Apply a version 1 default: debug a regression
    // A regression in Example B's new code makes one line read `Account legacy =
    // decode(encode(new Account("a1", 126, "ignored by v1"), 1));`. Repair it using the failing
    // assertion.
    // Expected: The unrepaired run fails with an `AssertionError` from the assertion on
    // `legacy.id().equals("a1") && legacy.cents() == 125 && legacy.note().equals("unlabelled")`;
    // the repaired line reads `Account legacy = decode(encode(new Account("a1", 125, "ignored by
    // v1"), 1));`.

    // Exercise 3: Reject an unknown version
    // Change the version bytes to 99 and decode.
    // Expected: IOException naming version.

    // Exercise 4: Detect truncation
    // Remove the final byte from a valid version 2 payload.
    // Expected: IOException or EOFException before returning a record.

    // Exercise 5: Reject an oversized declared text length
    // Replace the first text length with Integer.MAX_VALUE.
    // Expected: IOException for length before allocating that size.

    // Exercise 6: Reject trailing data and invalid domain state
    // Append an extra byte, then try constructing a negative-balance account.
    // Expected: trailing payload IOException; negative balance IllegalArgumentException.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
