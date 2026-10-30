// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Verify the domain summary
    // Summarize group A over amounts 10,20 and group B over 5.
    // Expected: A count 2, total 30; B count 1, total 5.

    // Exercise 2: Read a successful HTTPsummary
    // GET/summary?group=Afromtheownedserver.
    // Expected: status 200 andexactJSONwithcount2,total 30.

    // Exercise 3: Report an unknown valid group
    // GETgroupC,which passes syntax buthasnorecords.
    // Expected: status404 withnot_found error.

    // Exercise 4: Reject ambiguous or malformed queries
    // Send duplicate group parameters andalowercasegroup.
    // Expected: bothstatus400.

    // Exercise 5: Reject unsupported methods andpathlookalikes
    // POST to the summary route andGET/summary-extra.
    // Expected: 405 and404 respectively.

    // Exercise 6: Preserve storage and close the owned listener
    // Comparetherepositorybefore/afterrequests and close the server.
    // Expected: 3 unchanged records; closed flag true.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
