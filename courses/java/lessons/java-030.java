// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Round-trip version2 data
    // Encode accounta1,balance125,noteCafé withversion2 anddecode.
    // Expected: equal domain record andexact Unicode note.

    // Exercise 2: Apply a version1 default
    // Encode the same core fields usingversion1,which lacksnote.
    // Expected: decoded noteunlabelled.

    // Exercise 3: Reject an unknown version
    // Change theversion bytes to99 anddecode.
    // Expected: IOException namingversion.

    // Exercise 4: Detect truncation
    // Remove thefinalbyte from a validversion2payload.
    // Expected: IOException orEOFException before returning a record.

    // Exercise 5: Reject an oversized declared text length
    // Replace thefirsttextlength withInteger.MAX_VALUE.
    // Expected: IOException forlength before allocating thatsize.

    // Exercise 6: Reject trailing data andinvalid domain state
    // Append anextra byte,then try constructing a negative-balance account.
    // Expected: trailing payloadIOException;negative balanceIllegalArgumentException.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
