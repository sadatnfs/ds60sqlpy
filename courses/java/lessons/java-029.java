// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {

  public static void main(String[] args) throws Exception {
    // Exercise 1: Verify a real local database
    // Open the fixture,inspect product metadata andcount the two account rows.
    // Expected: database productH2;2 rows;auto-commit initiallytrue.

    // Exercise 2: Bind an injection-shaped value as data
    // Query byname usingAlice andthenAlicequoteOR1=1-shaped text through the same prepared
    // statement.
    // Expected: Alice matches1row;the injection-shaped value matches0.

    // Exercise 3: Roll back a transfer
    // Disableauto-commit,move20cents fromaccount1to2,inspect intermediate balances,androllback.
    // Expected: inside80,70;afterrollback100,50.

    // Exercise 4: Commit andread from a second session
    // Transfer10cents,commit,andopen another connection to the same owned memory database.
    // Expected: second connection sees90,60 andtotal150.

    // Exercise 5: Handle a constraint failure androllback
    // Attempt tosubtract200frombalance100,catch theSQL integrity error,androllback.
    // Expected: SQLState class23;balance remains100 afterrollback.

    // Exercise 6: Observe committed visibility under the declared isolation
    // Use twoH2connections atREAD_COMMITTED;updateaccount1 withoutcommit,read
    // fromtheother,thencommit andreadagain.
    // Expected: second session sees100beforecommit and95aftercommit.
    System.out.println("Implement and check the six exercises in your saved copy.");
  }
}
