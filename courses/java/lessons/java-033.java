// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Read an admitted owned file
    // Createinput.txt inside anownedroot andread atmost10bytes.
    // Expected: contenthello.

    // Exercise 2: Reject lexical traversal andabsolute paths
    // Attempt../outside.txt andanabsolutechildpath.
    // Expected: SecurityException forboth.

    // Exercise 3: Enforce the byte limit after reading a bounded amount
    // Writefivebytes andrequest a four-byte maximum.
    // Expected: IOException foroversizedcontent.

    // Exercise 4: Reject symbolic-link access under the declared policy
    // Create a link inside theownedroot toanotherownedfile andattempt toread throughit.
    // Expected: link rejected when platform supports creation;unsupported capability recorded explicitly.

    // Exercise 5: Keep operation names out ofcode execution
    // Admitonlyread_fixture andrejectrun_shell.
    // Expected: unknownoperationIllegalArgumentException.

    // Exercise 6: Build a restricted diagnostic record
    // Copy onlyrequest_id,operation andstatus from a map containingtoken andsource_text.
    // Expected: diagnostic excludes both sensitive fields.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
