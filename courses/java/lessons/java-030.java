// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Round-trip version 2 data: change one input
    // Close Example A and rebuild it in a fresh `Main.java`, keeping the assertion on
    // `decode(encoded).equals(record)`. Then propose one input change that would make that
    // assertion fail and explain why before trying it.
    // Expected: Your rebuild reproduces the worked observation (equal domain record and exact
    // Unicode note), and your proposed change makes the assertion on
    // `decode(encoded).equals(record)` fail.

    // Exercise 2: Apply a version 1 default: debug a regression
    // A regression changed one token in the code that Example B adds after Example A, so one
    // line now reads `Account legacy = decode(encode(new Account("a1", 126, "ignored by v1"),
    // 1));`. Run Example B with that line, use the failing assertion to locate the defect and
    // repair it without changing the assertion.
    // Expected: Before the repair the run fails with an `AssertionError` from the assertion on
    // `legacy.id().equals("a1") && legacy.cents() == 125 && legacy.note().equals("unlabelled")`;
    // after it the line reads `Account legacy = decode(encode(new Account("a1", 125, "ignored by
    // v1"), 1));` again and decoded note unlabelled.

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
