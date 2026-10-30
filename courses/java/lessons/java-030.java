// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Round-trip version 2 data
    // Encode account a1, balance 125, note Café with version 2 and decode.
    // Expected: equal domain record and exact Unicode note.

    // Exercise 2: Apply a version1 default
    // Encode the same core fields usingversion1,which lacks note.
    // Expected: decoded noteunlabelled.

    // Exercise 3: Reject an unknown version
    // Change the version bytes to99 and decode.
    // Expected: IOException naming version.

    // Exercise 4: Detect truncation
    // Remove the final byte from a validversion2payload.
    // Expected: IOException or EOFException before returning a record.

    // Exercise 5: Reject an oversized declared text length
    // Replace the first text length withInteger.MAX_VALUE.
    // Expected: IOException for length before allocating that size.

    // Exercise 6: Reject trailing data and invalid domain state
    // Append an extra byte,then try constructing a negative-balance account.
    // Expected: trailing payload IOException; negative balance IllegalArgumentException.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
