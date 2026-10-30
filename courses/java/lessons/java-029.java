// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Verify a real local database
    // Open the fixture,inspect product metadata and count the two account rows.
    // Expected: database product H2; 2 rows; auto-commit initially true.

    // Exercise 2: Bind an injection-shaped value as data
    // Query byname usingAlice andthenAlicequoteOR1=1-shaped text through the same prepared
    // statement.
    // Expected: Alice matches 1 row;the injection-shaped value matches0.

    // Exercise 3: Roll back a transfer
    // Disableauto-commit,move20cents fromaccount1to2,inspect intermediate balances,and rollback.
    // Expected: inside80,70;afterrollback100,50.

    // Exercise 4: Commit and read from a second session
    // Transfer10cents,commit,and open another connection to the same owned memory database.
    // Expected: second connection sees90,60 andtotal150.

    // Exercise 5: Handle a constraint failure and rollback
    // Attempt tosubtract200frombalance100,catch the SQL integrity error,and rollback.
    // Expected: SQLState class23;balance remains100 after rollback.

    // Exercise 6: Observe committed visibility under the declared isolation
    // Use twoH2connections atREAD_COMMITTED;updateaccount1 without commit,read from the
    // other,then commit and read again.
    // Expected: second session sees 100 before commit and 95 after commit.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
